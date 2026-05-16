"""
Main server module for the File Operations MCP Server.

This module initializes the FastMCP server, configures logging, and sets up
custom routes for health checks and monitoring.
"""

import logging
import os
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from .config import (
    SERVER_NAME, SERVER_VERSION, LOG_LEVEL, LOG_FORMAT,
    DEFAULT_ENCODING, MAX_FILE_SIZE
)
from .tools import register_all_tools

# Configure logging for the entire application
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_server(base_path: str = ".", encoding: str = DEFAULT_ENCODING, 
                 max_file_size: int = MAX_FILE_SIZE) -> FastMCP:
    """
    Create and configure the File Operations MCP server instance.
    
    This factory function:
    1. Creates the FastMCP server
    2. Registers all file operation tools
    3. Sets up custom HTTP routes for monitoring
    4. Returns the configured server
    
    Args:
        base_path: Base directory for file operations (default: current directory)
        encoding: Default file encoding (default: utf-8)
        max_file_size: Maximum file size in bytes (default: 10MB)
    
    Returns:
        FastMCP: Configured server instance ready to run
    """
    logger.info(f"Initializing {SERVER_NAME} v{SERVER_VERSION}")
    logger.info(f"Base path: {os.path.abspath(base_path)}")
    logger.info(f"Encoding: {encoding}, Max file size: {max_file_size} bytes")
    
    # Create the FastMCP server instance
    mcp = FastMCP("File Operations")
    
    # Register all file operation tools
    register_all_tools(mcp, base_path, encoding, max_file_size)
    
    # Add custom HTTP routes for debugging and health checks
    @mcp.custom_route("/", methods=["GET"])
    async def root(request):
        """
        Root endpoint - provides server information and available endpoints.
        """
        return JSONResponse({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "File Operations MCP Server - File system management",
            "status": "running",
            "config": {
                "base_path": os.path.abspath(base_path),
                "encoding": encoding,
                "max_file_size": max_file_size
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
            "version": SERVER_VERSION,
            "base_path": os.path.abspath(base_path)
        })
    
    @mcp.custom_route("/docs", methods=["GET"])
    async def docs(request):
        """
        Documentation endpoint - provides information about available tools.
        """
        return JSONResponse({
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "File system operations via MCP",
            "tools": {
                "reading": {
                    "read_file": "Read file contents with optional line range",
                    "get_file_info": "Get detailed file/directory information"
                },
                "writing": {
                    "write_file": "Write or append content to a file",
                    "delete_file": "Delete a file"
                },
                "directory_operations": {
                    "list_directory": "List files and directories with optional recursion",
                    "create_directory": "Create a new directory (with parents)"
                },
                "file_management": {
                    "copy_file": "Copy a file to a new location",
                    "move_file": "Move or rename a file"
                },
                "searching": {
                    "search_files": "Search for text patterns in files (regex supported)"
                }
            },
            "examples": {
                "read_file": 'read_file("config.json")',
                "write_file": 'write_file("output.txt", "Hello, World!")',
                "list_directory": 'list_directory("src", True, "*.py")',
                "search_files": 'search_files(".", "TODO", "*.js")',
                "copy_file": 'copy_file("file.txt", "backup/file.txt")',
                "move_file": 'move_file("old.txt", "new.txt")',
                "get_file_info": 'get_file_info("README.md")',
                "create_directory": 'create_directory("new_folder")',
                "delete_file": 'delete_file("temp.txt")'
            },
            "security": {
                "base_path_restriction": "All operations are restricted to the configured base path",
                "path_validation": "Paths are validated to prevent directory traversal attacks",
                "file_size_limits": f"Files larger than {max_file_size} bytes are rejected"
            }
        })
    
    logger.info("Server initialization complete")
    logger.info(f"Custom routes available: /, /health, /docs")
    return mcp

# Made with Bob