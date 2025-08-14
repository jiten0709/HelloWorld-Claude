from mcp_client import MCP_Client
from mcp.types import Tool, CallToolResult, TextContent
from typing import Optional, Literal, List
from anthropic.types import ToolResultBlockParam, Message
import json

class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCP_Client]) -> list[Tool]:
        """Gets all tools from the provided clients."""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools += [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                } for t in tool_models
            ]
        
        return tools
    
    @classmethod
    async def _find_client_with_tool(cls, clients: list[MCP_Client], tool_name: str) -> Optional[MCP_Client]:
        """Finds the first client that has the specified tool"""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
            
        return None
    
    @classmethod
    def _build_tool_result_part(
        cls,
        tool_use_id: str,
        text: str,
        status: Literal["success"] | Literal["error"],
    ) -> ToolResultBlockParam:
        """Builds a tool result part dictionary."""
        return {
            "tool_use_id": tool_use_id,
            "type": "tool_result",
            "content": text,
            "is_error": status == "error",
        }
    
    @classmethod
    async def execute_tool_requests(cls, clients: dict[str, MCP_Client], message: Message) -> List[ToolResultBlockParam]:
        """Executes a list of tool requests against the provided clients."""
        tool_requests = [block for block in message.content if block.type == "tool_use"]
        tool_result_blocks: list[ToolResultBlockParam] = []

        for tool_request in tool_requests:
            tool_id = tool_request.id
            tool_name = tool_request.name
            tool_input = tool_request.input

            client = await cls._find_client_with_tool(clients=list(clients.values()), tool_name=tool_name)

            if not client:
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id=tool_id,
                    text=f"Tool '{tool_name}' not found.",
                    status="error"
                )
                continue

            try:
                tool_output: CallToolResult = await client.call_tool(tool_name=tool_name, tool_input=tool_input)
                items = []
                if tool_output:
                    items = tool_output.content
                
                content_list = [item.text for item in items if isinstance(item, TextContent)]
                content_json = json.dumps(content_list)
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id=tool_id,
                    text=content_json,
                    status="error" if tool_output.isError else "success"
                )

            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {str(e)}"
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id=tool_id,
                    text=json.dumps({"error": error_message}),
                    status="error" if tool_output.isError else "success"
                )
            
            tool_result_blocks.append(tool_result_part)

        return tool_result_blocks