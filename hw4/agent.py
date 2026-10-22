"""Security analyst agent that uses two MCP servers at the same time.

Servers (both started over stdio by MultiServerMCPClient):
    secops_toolkit  my own server in mcp-server.py
    fetch           the published mcp-server-fetch server

The model is Gemini through ChatGoogleGenerativeAI. The model name comes from
GOOGLE_MODEL and the key comes only from GOOGLE_API_KEY. hw4/.env is loaded
if it exists. Based on 04_MCP/01_sqlite/01_stdio_mcp_client.py from the course
repo, without readline so it runs on Windows.

Usage:
    uv run python agent.py                  # interactive chat
    uv run python agent.py "your question"  # answer one question and exit
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

HERE = Path(__file__).resolve().parent

SERVERS = {
    "secops_toolkit": {
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "python", "mcp-server.py", "stdio"],
        "cwd": str(HERE),
    },
    "fetch": {
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "python", "-m", "mcp_server_fetch"],
        "cwd": str(HERE),
    },
}

# Long tool arguments (like a whole fetched page) are cut to this many chars.
ARG_PREVIEW = 200

SYSTEM_PROMPT = """You are a security analyst assistant.
For each request, first make a short plan of the steps. Then do the steps one at a time.
- Use the fetch tool to get web pages and API data. fetch returns only 5000
  characters by default. For JSON APIs and long records, call it with
  max_length=20000. If the result says the content was truncated, call fetch
  again with start_index set to the next character, until you have what you need.
- Use the secops_toolkit tools to analyze data: extract_iocs, cvss_to_severity,
  hash_text and password_strength.
- Pass the full fetched text to extract_iocs. Do not extract IOCs by hand.
- When the user asks for the incident_brief prompt, call get_incident_brief_prompt
  and answer every section it asks for.
- Use tool results for facts. Do not guess values that a tool can give you.
- If a tool fails, say what failed and why.
End with a short, clear answer for the user."""


def prompt_tool(client: MultiServerMCPClient) -> StructuredTool:
    """Wrap the incident_brief MCP prompt as a tool the model can call.

    MCP prompts are not tools, so the model cannot use them on its own.
    This tool gets the prompt text from the secops_toolkit server.

    Args:
        client: The connected MCP client.

    Returns:
        A tool named get_incident_brief_prompt.
    """

    async def get_incident_brief_prompt(cve_id: str) -> str:
        """Get the incident_brief prompt template for a CVE id, e.g. CVE-2021-44228."""
        messages = await client.get_prompt(
            "secops_toolkit", "incident_brief", arguments={"cve_id": cve_id}
        )
        return "\n".join(str(m.content) for m in messages)

    return StructuredTool.from_function(coroutine=get_incident_brief_prompt)


def build_llm() -> ChatGoogleGenerativeAI:
    """Create the Gemini chat model from environment variables.

    Returns:
        A ChatGoogleGenerativeAI model. It reads GOOGLE_API_KEY by itself.

    Raises:
        SystemExit: If GOOGLE_API_KEY or GOOGLE_MODEL is not set.
    """
    load_dotenv(HERE / ".env")
    if not os.getenv("GOOGLE_API_KEY"):
        sys.exit("GOOGLE_API_KEY is not set. Put it in hw4/.env (see .env.example).")
    model = os.getenv("GOOGLE_MODEL")
    if not model:
        sys.exit("GOOGLE_MODEL is not set. Put it in hw4/.env (see .env.example).")
    return ChatGoogleGenerativeAI(model=model)


def text_of(message: AIMessage) -> str:
    """Return the plain text of a model message.

    Gemini can return content as a string or as a list of parts.

    Args:
        message: The message from the model.

    Returns:
        The text parts joined together.
    """
    content = message.content
    if isinstance(content, str):
        return content
    parts = []
    for part in content:
        if isinstance(part, str):
            parts.append(part)
        elif isinstance(part, dict) and part.get("type") == "text":
            parts.append(part.get("text", ""))
    return "".join(parts)


def show_step(message) -> None:
    """Print one agent step: a tool call, a tool result, or the answer.

    Args:
        message: A message from the agent stream.
    """
    if isinstance(message, AIMessage) and message.tool_calls:
        for call in message.tool_calls:
            args = json.dumps(call["args"], ensure_ascii=False)
            if len(args) > ARG_PREVIEW:
                args = f"{args[:ARG_PREVIEW]}... ({len(args)} chars)"
            print(f"  [tool call] {call['name']}({args})")
    elif isinstance(message, ToolMessage):
        size = len(str(message.content))
        status = "error" if message.status == "error" else "ok"
        print(f"  [tool result] {message.name}: {status}, {size} chars")
    elif isinstance(message, AIMessage):
        print(f"\n{text_of(message)}\n")


async def ask(agent, question: str) -> None:
    """Run one question through the agent and print each step.

    Args:
        agent: The LangChain agent.
        question: The user's question.
    """
    async for update in agent.astream(
        {"messages": [("user", question)]}, stream_mode="updates"
    ):
        for step in update.values():
            for message in (step or {}).get("messages", []):
                show_step(message)


async def run_agent() -> None:
    """Start both MCP servers, build the agent, and run the chat loop."""
    llm = build_llm()
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools() + [prompt_tool(client)]
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

    print("Security analyst agent. Servers: " + ", ".join(SERVERS))
    print("Tools: " + ", ".join(tool.name for tool in tools))

    if len(sys.argv) > 1:
        try:
            await ask(agent, " ".join(sys.argv[1:]))
        except Exception as e:
            print(f"Error: {e}")
        return

    print("Type a question. Press Enter on an empty line to quit.")
    while True:
        line = input("llm>> ").strip()
        if not line:
            break
        try:
            await ask(agent, line)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_agent())
