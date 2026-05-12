"""
Main server module for the API Integration MCP Server.

This module initializes the FastMCP server, configures logging, and sets up
custom routes for health checks and monitoring.

Key Concepts:
- Separation of concerns: Server setup is separate from tool definitions
- The create_server() function returns a configured server instance
- Custom routes provide additional HTTP endpoints for monitoring
- Logging is configured once here and used throughout the application
"""

import logging
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from .config import SERVER_NAME, SERVER_VERSION, LOG_LEVEL, LOG_FORMAT
from .tools import register_all_tools

# Configure logging for the entire application
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """
    Create and configure the API Integration MCP server instance.
    
    This factory function:
    1. Creates the FastMCP server
    2. Registers all API integration tools
    3. Sets up custom HTTP routes for monitoring
    4. Returns the configured server
    
    Returns:
        FastMCP: Configured server instance ready to run
    """
    logger.info(f"Initializing {SERVER_NAME} v{SERVER_VERSION}")
    
    # Create the FastMCP server instance
    mcp = FastMCP("API Integration Hub")
    
    # Register all API integration tools
    register_all_tools(mcp)
    
    # Add custom HTTP routes for debugging and health checks
    @mcp.custom_route("/", methods=["GET"])
    async def root(request):
        """
        Root endpoint - provides server information and available endpoints.
        
        This is useful for:
        - Verifying the server is running
        - Discovering available endpoints
        - Getting server version information
        """
        return JSONResponse({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "API Integration MCP Server - Demonstrates various HTTP request types",
            "status": "running",
            "endpoints": {
                "sse": "/sse",
                "health": "/health",
                "docs": "/docs"
            },
            "tool_categories": {
                "weather": "GET requests to OpenWeatherMap API",
                "gists": "POST requests to GitHub Gist API",
                "trello": "PUT requests to Trello API",
                "storage": "DELETE requests to Cloudinary API",
                "github_graphql": "GraphQL queries to GitHub API"
            }
        })
    
    @mcp.custom_route("/health", methods=["GET"])
    async def health(request):
        """
        Health check endpoint - useful for monitoring and load balancers.
        
        Returns a simple status indicating the server is healthy and responsive.
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
        
        This helps users understand what the server can do without
        needing to connect via MCP protocol.
        """
        return JSONResponse({
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "tools": {
                "weather": {
                    "get_weather": "Get current weather for a city (GET request example)",
                    "get_forecast": "Get weather forecast for a city (GET request example)"
                },
                "github_gists": {
                    "create_gist": "Create a new GitHub Gist (POST request example)",
                    "create_multi_file_gist": "Create a gist with multiple files (POST request example)"
                },
                "trello": {
                    "update_trello_card": "Update a Trello card (PUT request example)",
                    "move_trello_card": "Move a card to a different list (PUT request example)",
                    "update_trello_card_labels": "Update card labels (PUT request example)"
                },
                "cloud_storage": {
                    "delete_image": "Delete an image from Cloudinary (DELETE request example)",
                    "delete_multiple_images": "Batch delete images (DELETE request example)",
                    "delete_images_by_prefix": "Delete images by prefix (DELETE request example)"
                },
                "github_graphql": {
                    "search_github_repositories": "Search repositories using GraphQL",
                    "get_github_user_profile": "Get user profile using GraphQL",
                    "get_github_repository_issues": "Get repository issues using GraphQL"
                }
            },
            "authentication": {
                "OPENWEATHER_API_KEY": "Required for weather tools",
                "GITHUB_TOKEN": "Required for GitHub tools (gists and GraphQL)",
                "TRELLO_API_KEY": "Required for Trello tools",
                "TRELLO_TOKEN": "Required for Trello tools",
                "CLOUDINARY_*": "Required for cloud storage tools"
            },
            "setup": "Set environment variables in .env file or system environment"
        })
    
    logger.info("Server initialization complete")
    logger.info(f"Custom routes available: /, /health, /docs")
    return mcp

# Made with Bob
