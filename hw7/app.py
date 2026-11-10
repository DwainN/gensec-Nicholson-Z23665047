"""Natural-language client for the HW7 nginx configuration MCP server."""
import asyncio
import os
import sys
from fast_agent.core.fastagent import FastAgent

fast = FastAgent("HW7 Nginx Agent", parse_cli_args=False)
@fast.agent(
    instruction="Use the nginx MCP tools to generate, validate, deploy, and inspect a lab web service. "
    "Always validate before deploying. Report real tool outcomes and limitations. "
    "Only manage the application-owned lab container. Do not claim deployment on failure.",
    model=os.environ.get("HW7_MODEL", "gemini-3.1-flash-lite-preview"),
    servers=["nginx"],
)
async def main():
    """Run an interactive session or one quoted request from the command line."""
    async with fast.run() as agent:
        if len(sys.argv) > 1:
            print(await agent.send(" ".join(sys.argv[1:])))
        else:
            await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
