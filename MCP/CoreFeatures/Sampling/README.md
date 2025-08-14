# MCP Sampling Example

A demonstration of Model Context Protocol (MCP) sampling functionality, showing how an MCP server can call back to the client's AI model for processing.

## Overview

This example implements a simple summarization service using MCP's sampling feature. The client provides a sampling callback that allows the MCP server to request AI model responses during tool execution.

## Architecture

```
Client (with Claude API) ←→ MCP Server
     ↑                           ↓
     └── Sampling Callback ←─────┘
```

1. **Client** (`client.py`): Connects to Anthropic's Claude API and provides sampling callback
2. **Server** (`server.py`): Exposes a `summarize` tool that uses sampling to generate summaries

## Files

- `client.py` - MCP client with Anthropic integration and sampling callback
- `server.py` - MCP server with summarization tool
- `.env` - Environment variables (not included, see setup)

## Prerequisites

1. **Python Environment**:

   ```bash
   # Using uv (recommended)
   uv add anthropic mcp

   # Or using pip
   pip install anthropic mcp python-dotenv
   ```

2. **API Key**: Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)

3. **Environment Variables**: Create a `.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## How to Run

```bash
# Using uv (recommended)
uv run client.py

# Or using Python directly
python client.py
```

## How It Works

1. **Client starts the server**: Uses `uv run server.py` via stdio
2. **Establishes MCP connection**: Client connects to server over stdio
3. **Calls summarize tool**: Sends text to be summarized
4. **Server requests sampling**: Server calls back to client via sampling callback
5. **Client processes with Claude**: Client sends request to Anthropic's API
6. **Returns result**: Summary flows back through the chain

## Key Components

### Sampling Callback

```python
async def sampling_callback(context: RequestContext, params: CreateMessageRequestParams):
    text = await chat(params.messages)
    return CreateMessageResult(
        role="assistant",
        model=MODEL,
        content=TextContent(type="text", text=text),
    )
```

### Server Tool

```python
@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):
    result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user", content=TextContent(type="text", text=prompt))],
        max_tokens=4000,
        system_prompt="You are a helpful research assistant.",
    )
    return result.content.text
```

## Configuration

- **Model**: Claude 3.5 Haiku (`claude-3-5-haiku-20241022`)
- **Max Tokens**: 4000
- **Transport**: stdio

## Example Usage

The client includes a sample resume text that gets summarized when you run the script. You can modify the `doc` variable in `client.py` to test with your own content.

## Troubleshooting

**"Error loading .env file"**: Make sure you have a `.env` file with your `ANTHROPIC_API_KEY`

**"No text was provided"**: The server expects actual text content, not placeholder strings

**Connection errors**: Ensure `uv` is installed and the server starts correctly

## Learning Points

- **MCP Sampling**: How servers can request AI model inference from clients
- **Async Communication**: Bidirectional communication between client and server
- **Tool Definition**: Creating MCP tools with context access
- **Error Handling**: Managing API errors and connection issues

This example demonstrates the power of MCP's sampling feature, enabling servers to leverage the client's AI capabilities while maintaining clear separation
