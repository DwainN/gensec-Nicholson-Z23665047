# HW7: nginx Configuration Agent

A Python natural-language agent uses a custom MCP server to generate a bounded nginx configuration, check it with nginx, deploy it in Docker, and inspect its health.

## Checkout

```bash
git clone --branch hw7-nginx-agent https://github.com/DwainN/gensec-Nicholson-Z23665047.git hw7-recording
cd hw7-recording/hw7
uv sync
```

## Run

On the course Kali VM:

```bash
cd ~/gensec-Nicholson-Z23665047/hw7
uv sync
export GOOGLE_API_KEY='your existing key'
uv run app.py
```

Keep the key in your environment; never commit it. If it is already exported, do not export it again. The model can be selected with HW7_MODEL; the current default is gemini-3.1-flash-lite-preview. Availability and free quotas depend on the provider.

Example request:

> Generate a service saying Hello from Dwain HW7. Validate the configuration, deploy it, and check its health.

If the named container already exists, ask the agent to stop the lab service before deploying again.

```bash
curl http://127.0.0.1:8087
curl http://127.0.0.1:8087/health
uv run python test_mcp.py
```

The integration test uses actual MCP calls and Docker. It checks generation, invalid input rejection, nginx syntax, deployment, health, and duplicate deployment rejection. It replaces only the named disposable lab container and leaves it running for demonstration.

## Files

- app.py: FastAgent client, environment-selected model, interactive or one-shot request.
- server.py: five MCP tools, bounded configuration inputs, subprocess time limits, nginx validation.
- test_mcp.py: end-to-end MCP transport and deployment verification.
- fastagent.config.yaml: local stdio MCP server connection.
- pyproject.toml: tested dependency minimum versions; uv sync resolves dependencies.
- screencast_url.txt: replace with the unlisted MediaSpace URL after recording.

## Design and limitations

The model chooses structured tool arguments. Python constructs the configuration from those arguments; it does not execute arbitrary model-generated shell commands. Docker commands use fixed argument lists with no shell. Only dwain-hw7-nginx is managed. The service is bound to loopback, uses an unprivileged user, drops Linux capabilities, and uses a read-only container filesystem with temporary writable storage.

This prototype supports plain-text responses and hostname selection, not arbitrary nginx directives, TLS, public hosting, multiple services, or automatic updates. It requires Docker and permission to use sudo -n docker on the lab VM. Docker access is privileged; this is a local coursework prototype. The API may be rate limited or unavailable. Direct MCP tests do not require an LLM key but do not establish that a model-driven run succeeded.

The exact image tag can change over time; the repository specifies dependency minimums and does not pin the container image digest.

## Screencast: under five minutes

1. Camera on initially. Introduce the app and its purpose (0:00–0:20).
2. Show source checkout from the course repository into a fresh temporary folder, then cd to hw7 and uv sync (0:20–0:50). Use `git remote get-url origin` privately to obtain your actual course repository URL; never show a URL containing credentials.
3. Run the app and request generation, validation, deployment, and health. Show curl output (0:50–2:20). If the API is blocked, show the error honestly and demonstrate the tools with test_mcp.py; finish a model-driven demonstration when access is available.
4. Demonstrate rejected input and duplicate deployment using test_mcp.py (2:20–3:05).
5. In GitLab show the incremental commits. Explain server.py, app.py, config, and tests, including validation and isolation (3:05–4:30).
6. State limitations and finish before five minutes (4:30–4:50).
7. Upload to MediaSpace as Unlisted, put the URL in screencast_url.txt, commit and push before class.
