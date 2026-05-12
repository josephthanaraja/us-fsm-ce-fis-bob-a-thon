import logging
import sys
from fastmcp import FastMCP
from starlette.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("basic-mcp-server")

mcp = FastMCP("Simple Calculator")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    logger.info(f"Tool called: add({a}, {b})")
    return a + b

@mcp.custom_route("/", methods=["GET"])
async def root(request):
    return JSONResponse({
        "status": "ok",
        "message": "Basic MCP Server is running",
        "transport": "stdio"
    })

if __name__ == "__main__":
    logger.info("Starting MCP Server on port 8080...")
    try:
        mcp.run(transport="stdio", show_banner=False)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Server terminated")

# Made with Bob
