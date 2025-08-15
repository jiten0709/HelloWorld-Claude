from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import LoggingMessageNotificationParams

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

server_parmas = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)

async def logging_callback(params: LoggingMessageNotificationParams):
    logger.info(f"Client: {params.data}")

async def print_progress_callback(progress: float, total: float | None, message: str | None):
    if total is not None:
        percentage = (progress / total) * 100
        logger.info(f"Client: Progress: {progress}/{total} ({percentage:.2f}%)")
    else:
        logger.info(f"Client: Progress: {progress}")

async def run():
    async with stdio_client(server_parmas) as (read, write):
        async with ClientSession(
            read, write, logging_callback=logging_callback
        ) as session:
            await session.initialize()

            res = await session.call_tool(
                name="add",
                arguments={"a": 1, "b": 3},
                progress_callback=print_progress_callback,
            )

            logger.info(f"Client: Result of add: {res.content[0].text}")

if __name__ == "__main__":
    import asyncio

    logger.info("Starting client...")
    asyncio.run(run())
    logger.info("Client finished.")