# MCP Notifications Example

A demonstration of Model Context Protocol (MCP) notifications and progress reporting between client and server.

## Overview

This example shows how an MCP server can send logging messages and progress updates to the client during tool execution.

## Files

- `client.py` - MCP client with logging and progress callbacks
- `server.py` - MCP server with notification-enabled tool

## How to Run

```bash
uv run client.py
```

## What It Does

1. Client calls the `add` tool with arguments `{a: 1, b: 3}`
2. Server sends logging notifications and progress updates during execution
3. Client receives and displays the notifications and progress
4. Returns the result: `4`

## Key Features

- **Logging Notifications**: Server sends info messages to client
- **Progress Reporting**: Server reports completion percentage
- **Async Communication**: Real-time updates during tool execution

## Expected Output

```
Starting client...
Client: Preparing to add...
Client: Progress: 20.0/100 (20.00%)
Client: OK, adding...
Client: Progress: 80.0/100 (80.00%)
Client: Result of add: 4
Client finished.
```

This demonstrates how MCP enables rich communication patterns beyond simple request-response.
