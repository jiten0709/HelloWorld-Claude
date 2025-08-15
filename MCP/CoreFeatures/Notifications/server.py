from mcp.server.fastmcp import FastMCP, Context
import asyncio

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    # handlers=[
    #     logging.StreamHandler(),
    #     logging.FileHandler('server.log', mode='w')
    # ]
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name='Notifications Server')

@mcp.tool()
async def add(a: int, b: int, ctx: Context) -> int:
    logger.info("Server: Preparing to add...")
    await ctx.info("Preparing to add...")
    await ctx.report_progress(20, 100)
    await asyncio.sleep(2)
    await ctx.info("OK, adding...")
    await ctx.report_progress(80, 100)

    return a + b

if __name__ == "__main__":
    mcp.run(transport="stdio")
    logger.info("Server is running...")