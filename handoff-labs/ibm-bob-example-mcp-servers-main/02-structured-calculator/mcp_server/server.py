import logging
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from .config import SERVER_NAME, SERVER_VERSION, LOG_LEVEL, LOG_FORMAT
from .tools import register_all_tools

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_server() -> FastMCP:
    logger.info(f"Initializing {SERVER_NAME} v{SERVER_VERSION}")
    
    mcp = FastMCP("Structured Calculator")
    register_all_tools(mcp)
    
    @mcp.custom_route("/", methods=["GET"])
    async def root(request):
        return JSONResponse({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "status": "running",
            "endpoints": {
                "sse": "/sse",
                "health": "/health"
            }
        })
    
    @mcp.custom_route("/health", methods=["GET"])
    async def health(request):
        return JSONResponse({
            "status": "healthy",
            "server": SERVER_NAME,
            "version": SERVER_VERSION
        })
    
    logger.info("Server initialization complete")
    return mcp

# Made with Bob
