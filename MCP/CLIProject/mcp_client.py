from typing import Optional, Any
from mcp import ClientSession, StdioServerParameters, types
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl
import json
import asyncio

class MCP_Client:
    def __init__(
            self,
            command: str,
            args: list[str],
            env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server=server_params))
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(ClientSession(_stdio, _write))
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect first."
            )
        return self._session
    
    async def list_tools(self) -> list[types.Tool]:
        results = await self.session().list_tools()
        return results.tools

    async def call_tool(self, tool_name: str, tool_input) -> types.CallToolResult | None:
        return await self.session().call_tool(tool_name, tool_input)

    async def list_prompts(self) -> list[types.Prompt]:
        results = await self.session().list_prompts()
        return results.prompts

    async def get_prompt(self, prompt_name: str, args: dict[str, str]):
        results = await self.session().get_prompt(prompt_name, args)
        return results.messages

    async def read_resource(self, uri: str) -> Any:
        results = await self.session().read_resource(AnyUrl(uri))
        resource = results.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            
            return resource.text

    async def cleanup(self):
        await self._exit_stack.aclose()

    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

# for testing purposes
async def main():
    async with MCP_Client(
        command="uv",
        args=["run", "mcp_server.py"],
    ) as _client:
        pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())