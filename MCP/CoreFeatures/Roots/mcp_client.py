from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.types import Root, ListRootsResult, ErrorData
from mcp.shared.context import RequestContext
from pathlib import Path
from pydantic import FileUrl

import json
from pydantic import AnyUrl

import logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_client.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
        roots: Optional[list[str]] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._roots = self._create_roots(roots) if roots else []
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    def _create_roots(self, root_paths: list[str]) -> list[Root]:
        """Convert path strings to Root objects."""
        logger.info(f"Creating roots from paths: {root_paths}")
        roots = []
        for path in root_paths:
            p = Path(path).resolve()
            file_url = FileUrl(f"file://{p}")
            roots.append(Root(uri=file_url, name=p.name or "Root"))
        return roots

    async def _handle_list_roots(
        self, context: RequestContext["ClientSession", None]
    ) -> ListRootsResult | ErrorData:
        """Callback for when server requests roots."""
        logger.info("Handling list roots request")
        return ListRootsResult(roots=self._roots)

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(
                _stdio,
                _write,
                list_roots_callback=self._handle_list_roots
                if self._roots
                else None,
            )
        )
        await self._session.initialize()
        logger.info("MCP Client connected to server")

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        logger.info("Returning current session")

        return self._session

    async def list_tools(self) -> list[types.Tool]:
        """List all tools available in the current session."""
        logger.info("Listing all tools in the current session")
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input
    ) -> types.CallToolResult | None:
        """Call a specific tool with the provided input."""
        logger.info(f"Calling tool: {tool_name} with input: {tool_input}")
        return await self.session().call_tool(tool_name, tool_input)

    async def list_prompts(self) -> list[types.Prompt]:
        """List all prompts available in the current session."""
        logger.info("Listing all prompts in the current session")
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        """Get a specific prompt by name with the provided arguments."""
        logger.info(f"Getting prompt: {prompt_name} with args: {args}")
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the server by its URI."""
        logger.info(f"Reading resource from URI: {uri}")
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)

            return resource.text

    async def cleanup(self):
        """Clean up resources and close the session."""
        logger.info("Cleaning up MCP Client resources")
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        """Context manager entry point."""
        logger.info("Entering MCP Client context")
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        logger.info("Exiting MCP Client context")
        await self.cleanup()
