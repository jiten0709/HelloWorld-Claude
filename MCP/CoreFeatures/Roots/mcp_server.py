from pathlib import Path
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp import Context
from core.video_converter import VideoConverter
from core.utils import file_url_to_path

import logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_server.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

mcp = FastMCP("VidsMCP", log_level="ERROR")


async def is_path_allowed(requested_path: Path, ctx: Context) -> bool:
    logger.info(f"Checking if path {requested_path} is allowed...")

    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots

    if not requested_path.exists():
        logger.warning(f"Requested path does not exist: {requested_path}")
        return False

    if requested_path.is_file():
        requested_path = requested_path.parent

    for root in client_roots:
        root_path = file_url_to_path(root.uri)
        try:
            requested_path.relative_to(root_path)
            logger.info(f"Path {requested_path} is within root {root_path}")
            return True
        except ValueError:
            continue

    logger.warning(f"Path {requested_path} is not within any root directories")
    return False


@mcp.tool()
async def convert_video(
    input_path: str = Field(description="Path to the input MP4 file"),
    format: str = Field(description="Output format (e.g. 'mov')"),
    *,
    ctx: Context,
):
    """Convert an MP4 video file to another format using ffmpeg"""
    logger.info(f"Converting video {input_path} to format {format}")

    input_file = VideoConverter.validate_input(input_path)

    # Ensure the input file is contained in a root
    if not await is_path_allowed(input_file, ctx):
        raise ValueError(f"Access to path is not allowed: {input_path}")

    return await VideoConverter.convert(input_path, format)


@mcp.tool()
async def list_roots(ctx: Context):
    """
    List all directories that are accessible to this server.
    These are the root directories where files can be read from or written to.
    """
    logger.info("Listing all accessible root directories...")

    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots

    return [file_url_to_path(root.uri) for root in client_roots]


@mcp.tool()
async def read_dir(
    path: str = Field(description="Path to a directory to read"),
    *,
    ctx: Context,
):
    """Read directory contents. Path must be within one of the client's roots."""
    logger.info(f"Reading directory contents for path: {path}")

    requested_path = Path(path).resolve()

    if not await is_path_allowed(requested_path, ctx):
        raise ValueError("Error: can only read directories within a root")

    return [entry.name for entry in requested_path.iterdir()]


if __name__ == "__main__":
    mcp.run(transport="stdio")
