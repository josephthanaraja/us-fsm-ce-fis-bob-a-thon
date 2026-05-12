"""
Main server module for the Code Execution Sandbox MCP Server.

This module initializes the FastMCP server, configures logging, and sets up
custom routes for health checks and monitoring.
"""

import logging
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from .config import (
    SERVER_NAME, SERVER_VERSION, LOG_LEVEL, LOG_FORMAT,
    DEFAULT_TIMEOUT, MAX_OUTPUT_SIZE, SUPPORTED_LANGUAGES
)
from .tools import register_all_tools

# Configure logging for the entire application
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_server(timeout: int = DEFAULT_TIMEOUT, max_output_size: int = MAX_OUTPUT_SIZE) -> FastMCP:
    """
    Create and configure the Code Execution Sandbox MCP server instance.
    
    This factory function:
    1. Creates the FastMCP server
    2. Registers all code execution tools
    3. Sets up custom HTTP routes for monitoring
    4. Returns the configured server
    
    Args:
        timeout: Execution timeout in seconds
        max_output_size: Maximum output size in bytes
    
    Returns:
        FastMCP: Configured server instance ready to run
    """
    logger.info(f"Initializing {SERVER_NAME} v{SERVER_VERSION}")
    logger.info(f"Timeout: {timeout}s, Max output: {max_output_size} bytes")
    logger.info(f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}")
    
    # Create the FastMCP server instance
    mcp = FastMCP(
        "Code Execution Sandbox",
        stateless_http=True,
    )
    
    # Register all code execution tools
    register_all_tools(mcp, timeout, max_output_size)
    
    # Add custom HTTP routes for debugging and health checks
    @mcp.custom_route("/", methods=["GET"])
    async def root(request):
        """
        Root endpoint - provides server information and available endpoints.
        """
        return JSONResponse({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "Code Execution Sandbox - Safe code execution in containers",
            "status": "running",
            "config": {
                "timeout": timeout,
                "max_output_size": max_output_size,
                "supported_languages": SUPPORTED_LANGUAGES
            },
            "endpoints": {
                "mcp": "/mcp",
                "health": "/health",
                "docs": "/docs"
            },
            "security": {
                "containerized": True,
                "non_root_user": True,
                "resource_limits": True
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
            "description": "Safe code execution in isolated container environment",
            "tools": {
                "python": {
                    "execute_python": "Execute Python code with stdin support"
                },
                "javascript": {
                    "execute_javascript": "Execute JavaScript/Node.js code with stdin support"
                },
                "bash": {
                    "execute_bash": "Execute Bash scripts"
                },
                "system": {
                    "execute_command": "Execute shell commands with arguments"
                }
            },
            "examples": {
                "execute_python": 'execute_python("print(\'Hello, World!\')")',
                "execute_javascript": 'execute_javascript("console.log(\'Hello, World!\');")',
                "execute_bash": 'execute_bash("echo \'Hello, World!\'")',
                "execute_command": 'execute_command("ls", "-la")'
            },
            "security_features": [
                "Runs in Docker container with resource limits",
                "Non-root user execution",
                "Timeout protection",
                "Output size limits",
                "Isolated file system",
                "No network access (configurable)"
            ],
            "limits": {
                "timeout_seconds": timeout,
                "max_output_bytes": max_output_size,
                "memory_limit": "256MB",
                "cpu_limit": "1.0 cores"
            }
        })
    
    logger.info("Server initialization complete")
    logger.info(f"Custom routes available: /, /health, /docs")
    return mcp

# Made with Bob