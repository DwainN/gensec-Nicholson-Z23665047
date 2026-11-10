"""Exercise the actual MCP transport, nginx validator, deployment, and limits."""
import asyncio
import json
from fastmcp import Client

def payload(result):
    """Decode the structured JSON tool response for assertions."""
    if result.structured_content is not None:
        return result.structured_content
    return json.loads(result.content[0].text)

async def main():
    """Run a disposable end-to-end test, retaining a healthy service for the demo."""
    async with Client("server.py") as client:
        tools = await client.list_tools()
        print("TOOLS", [tool.name for tool in tools])
        generated = payload(await client.call_tool("generate_config", {"message": "Hello from Dwain HW7"}))
        assert "listen 8080" in generated["configuration"]
        print("GENERATE PASS", generated["sha256"])
        rejected = await client.call_tool("generate_config", {"message": "bad; directive"}, raise_on_error=False)
        assert rejected.is_error
        print("INVALID INPUT REJECTED")
        valid = payload(await client.call_tool("validate_config"))
        assert valid["returncode"] == 0, valid
        print("NGINX SYNTAX PASS", valid)
        await client.call_tool("stop_service")
        deployed = payload(await client.call_tool("deploy_config"))
        assert deployed["deployed"], deployed
        print("DEPLOY PASS", deployed)
        await asyncio.sleep(1)
        status = payload(await client.call_tool("service_status"))
        assert status["health"]["status"] == 200, status
        print("HEALTH PASS", status)
        duplicate = payload(await client.call_tool("deploy_config"))
        assert not duplicate["deployed"]
        print("DUPLICATE DEPLOY REJECTED")
        print("ALL MCP TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(main())
