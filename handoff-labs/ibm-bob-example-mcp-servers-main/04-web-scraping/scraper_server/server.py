"""
Main server module for the Web Scraping MCP Server.

This module initializes the FastMCP server, configures logging, and sets up
custom routes for health checks and monitoring.
"""

import logging
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from .config import (
    SERVER_NAME, SERVER_VERSION, LOG_LEVEL, LOG_FORMAT,
    DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
)
from .tools import register_all_tools

# Configure logging for the entire application
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_server(timeout: int = DEFAULT_TIMEOUT, user_agent: str = DEFAULT_USER_AGENT) -> FastMCP:
    """
    Create and configure the Web Scraping MCP server instance.
    
    This factory function:
    1. Creates the FastMCP server
    2. Registers all web scraping tools
    3. Sets up custom HTTP routes for monitoring
    4. Returns the configured server
    
    Args:
        timeout: Request timeout in seconds
        user_agent: User agent string for HTTP requests
    
    Returns:
        FastMCP: Configured server instance ready to run
    """
    logger.info(f"Initializing {SERVER_NAME} v{SERVER_VERSION}")
    logger.info(f"Timeout: {timeout}s, User-Agent: {user_agent[:50]}...")
    
    # Create the FastMCP server instance
    mcp = FastMCP("Web Scraper")
    
    # Register all web scraping tools
    register_all_tools(mcp, timeout, user_agent)
    
    # Add custom HTTP routes for debugging and health checks
    @mcp.custom_route("/", methods=["GET"])
    async def root(request):
        """
        Root endpoint - provides server information and available endpoints.
        """
        return JSONResponse({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "Web Scraping MCP Server - Fetch and parse web content",
            "status": "running",
            "config": {
                "timeout": timeout,
                "user_agent": user_agent[:50] + "..."
            },
            "endpoints": {
                "sse": "/sse",
                "health": "/health",
                "docs": "/docs"
            }
        })
    
    @mcp.custom_route("/health", methods=["GET"])
    async def health(request):
        """
        Health check endpoint - useful for monitoring and load balancers.
        """
        return JSONResponse({
            "status": "healthy",
            "server": SERVER_NAME,
            "version": SERVER_VERSION
        })
    
    @mcp.custom_route("/docs", methods=["GET"])
    async def docs(request):
        """
        Documentation endpoint - provides information about available tools.
        """
        return JSONResponse({
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "Web scraping and content extraction via MCP",
            "tools": {
                "content_fetching": {
                    "fetch_webpage": "Fetch full HTML content from a URL",
                    "extract_text": "Extract clean text content from a webpage",
                    "extract_metadata": "Extract page metadata (title, description, Open Graph, etc.)"
                },
                "link_extraction": {
                    "extract_links": "Extract all links from a webpage with optional filtering",
                    "extract_images": "Extract all images with optional size filtering"
                },
                "structured_data": {
                    "extract_structured_data": "Extract data from specific elements using CSS selectors",
                    "extract_tables": "Extract table data from webpages"
                }
            },
            "examples": {
                "fetch_webpage": 'fetch_webpage("https://example.com")',
                "extract_links": 'extract_links("https://example.com", r".*\\.pdf$")',
                "extract_text": 'extract_text("https://example.com", "article p")',
                "extract_metadata": 'extract_metadata("https://example.com")',
                "extract_images": 'extract_images("https://example.com", 300, 300)',
                "extract_structured_data": 'extract_structured_data("https://news.com", "h2.headline a", \'["text", "href"]\')',
                "extract_tables": 'extract_tables("https://example.com", 0)'
            },
            "features": [
                "Automatic URL resolution (relative to absolute)",
                "Custom HTTP headers support",
                "CSS selector-based extraction",
                "Regex filtering for links",
                "Image size filtering",
                "Table parsing",
                "Metadata extraction (Open Graph, Twitter Cards)",
                "Clean text extraction"
            ]
        })
    
    logger.info("Server initialization complete")
    logger.info(f"Custom routes available: /, /health, /docs")
    return mcp

# Made with Bob