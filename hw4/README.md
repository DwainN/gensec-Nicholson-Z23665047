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

## Limitations

- **fetch cannot run JavaScript.** It gets the raw HTML only. Pages that build their content with JS come back empty or partial.
- **fetch returns 5000 characters per call by default.** Long pages and JSON records are cut off. The agent must use `max_length` or `start_index`. The CVE-2021-44228 record has its CVSS score near character 17800.
- **The model can be wrong.** It can skip a step, misread data, or invent a value. Tool results are facts. The final text is not, so check it.
- **SSRF risk (server-side request forgery).** The fetch server can request any URL, including `localhost`, the private network and cloud metadata (`169.254.169.254`). An attacker who controls the prompt or a fetched page could use the agent to reach internal systems.
- **Prompt injection.** A fetched page can hide instructions for the model. [demo/injected_page.html](demo/injected_page.html) has hidden white text that tells the agent to ignore the user and print a fake "ALL CLEAR".
- **Free-tier quota.** About 20 requests per model per day.

### Defenses in agent.py

- **URL guard.** `check_url` runs before every fetch call. It allows only `http` and `https`. It blocks `localhost` and any host that resolves to a non-public address (loopback, private, link-local, metadata). Tests: [tests/test_url_guard.py](tests/test_url_guard.py).
- **Fetched content is data.** The system prompt tells the model that fetched text is never an instruction, and to report injection attempts.
- These are not complete. A system prompt does not stop every injection. The guard checks DNS once, but the fetch server resolves the name again (DNS rebinding) and follows redirects by itself.

### Demo the guard

```bash
uv run python -m http.server 8000      # in hw4, in a second terminal
uv run python agent.py "Fetch http://localhost:8000/demo/injected_page.html and summarize it."
```

The guard prints `[url guard] blocked ... localhost is not allowed`, and the model never sees the page.

## Why I trusted mcp-server-fetch

- It is the **official reference server** from the [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) repo, which maintains MCP itself.
- It is **published by Anthropic on PyPI** as [mcp-server-fetch](https://pypi.org/project/mcp-server-fetch/).
- It is **pinned** to `mcp-server-fetch==2026.8.18`, an older release, in [pyproject.toml](pyproject.toml), and `uv.lock` records the exact hashes. A new, compromised release cannot get in by itself.
- The code is small and open, so I can read it.

## Files

- [agent.py](agent.py): the agent and the chat loop.
- [mcp-server.py](mcp-server.py): the `secops_toolkit` MCP server.
- [tests/test_server.py](tests/test_server.py): unit tests for the server tools.
- [.env.example](.env.example): the environment variables. The real `.env` is git-ignored.
