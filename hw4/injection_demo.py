"""HW5 demo harness for an authorized pen test of the HW4 agent.

This runs the UNMODIFIED HW4 agent (same system prompt, same Gemini model,
same tools) but relaxes ONE thing: it allows localhost so the attack page can
be served offline, without publishing it to the public internet.

Why this is faithful: the prompt-injection flaw being demonstrated lives in how
the model treats fetched text. It does not depend on where the page is hosted.
On a real public URL (which the agent is designed to fetch) the same page would
trigger the same injection. The real agent.py URL guard still blocks localhost
as an SSRF defense; this harness relaxes only that one check so the demo can run
with no network and no public upload.

Usage:
    uv run python injection_demo.py "Fetch http://localhost:8000/... and ..."
"""

import asyncio

import agent  # the real HW4 agent module

# Neutralize ONLY the URL guard: check_url now returns None for EVERY url, so the
# local test page is reachable offline. No other code is changed; the system
# prompt, model, and tools are exactly agent.py. The injection/data-poisoning
# flaw under test is in how the model treats fetched text, not where it is hosted.
agent.check_url = lambda url: None

if __name__ == "__main__":
    asyncio.run(agent.run_agent())
