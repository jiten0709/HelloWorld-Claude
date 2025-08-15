from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    # handlers=[
    #     logging.StreamHandler(), 
    #     logging.FileHandler('server.log', mode='w')  
    # ]
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name='Sampling Server')

@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):
    logger.info("Starting summarization...")

    prompt = f"""
        Please summarize the following text:
        {text_to_summarize}
    """

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user", content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=4000,
        system_prompt="You are a helpful research assistant.",
    )

    if result.content.type == "text":
        return result.content.text
    else:
        raise ValueError("Sampling failed")
    
if __name__ == "__main__":
    mcp.run(transport="stdio")
    