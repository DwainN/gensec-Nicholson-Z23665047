# Homework 4: MCP security analyst agent

Dwain Nicholson, Z23665047

A LangChain agent (Gemini) that uses two MCP servers at the same time:

| Server | What it is | Tools |
| --- | --- | --- |
| `secops_toolkit` | My own FastMCP server, [mcp-server.py](mcp-server.py) | `extract_iocs`, `cvss_to_severity`, `hash_text`, `password_strength`, prompt `incident_brief` |
| `fetch` | The published [mcp-server-fetch](https://pypi.org/project/mcp-server-fetch/) server | `fetch` |

The agent plans multi-step work. It uses `fetch` to get web data and `secops_toolkit` to analyze it. It prints each tool call and its arguments.

## Run it

You need [uv](https://docs.astral.sh/uv/) and a Gemini API key from https://aistudio.google.com/apikey.

```bash
git clone https://github.com/DwainN/gensec-Nicholson-Z23665047.git
cd gensec-Nicholson-Z23665047/hw4
uv sync
cp .env.example .env        # then put your key after GOOGLE_API_KEY=
uv run python agent.py
```

Use `GOOGLE_MODEL=gemini-3.5-flash`. New API keys can no longer use `gemini-2.5-flash` (404 NOT_FOUND). The free tier allows about 20 requests per model per day, and one multi-step task uses about 5.

Type a question at the `llm>>` prompt. Press Enter on an empty line to quit.

To ask one question and exit:

```bash
uv run python agent.py "Rate the password Summer2024!"
```

The agent starts both servers by itself over stdio. You do not start them by hand.

## Run the server alone

```bash
uv run python mcp-server.py stdio   # for an MCP client
uv run python mcp-server.py http    # http://127.0.0.1:8080/mcp
```

## Tests

```bash
uv run pytest
```

## Files

- [agent.py](agent.py): the agent and the chat loop.
- [mcp-server.py](mcp-server.py): the `secops_toolkit` MCP server.
- [tests/test_server.py](tests/test_server.py): unit tests for the server tools.
- [.env.example](.env.example): the environment variables. The real `.env` is git-ignored.
