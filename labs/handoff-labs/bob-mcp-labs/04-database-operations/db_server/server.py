"""
Main server module for the Database Operations MCP Server.

This module initializes the FastMCP server, configures logging, and sets up
custom routes for health checks and monitoring.
"""

import logging
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from .config import SERVER_NAME, SERVER_VERSION, LOG_LEVEL, LOG_FORMAT, DEFAULT_DB_PATH
from .tools import register_all_tools

# Configure logging for the entire application
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_server(db_path: str = DEFAULT_DB_PATH) -> FastMCP:
    """
    Create and configure the Database Operations MCP server instance.
    
    This factory function:
    1. Creates the FastMCP server
    2. Registers all database operation tools
    3. Sets up custom HTTP routes for monitoring
    4. Returns the configured server
    
    Args:
        db_path: Path to the SQLite database file (default: example.db)
    
    Returns:
        FastMCP: Configured server instance ready to run
    """
    logger.info(f"Initializing {SERVER_NAME} v{SERVER_VERSION}")
    logger.info(f"Database path: {db_path}")
    
    # Create the FastMCP server instance
    mcp = FastMCP("Database Operations")
    
    # Register all database tools
    register_all_tools(mcp, db_path)
    
    # Add custom HTTP routes for debugging and health checks
    @mcp.custom_route("/", methods=["GET"])
    async def root(request):
        """
        Root endpoint - provides server information and available endpoints.
        """
        return JSONResponse({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "Database Operations MCP Server - SQLite database management",
            "status": "running",
            "database": db_path,
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
            "database": db_path
        })
    
    @mcp.custom_route("/docs", methods=["GET"])
    async def docs(request):
        """
        Documentation endpoint - provides information about available tools.
        """
        return JSONResponse({
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": "SQLite database operations via MCP",
            "tools": {
                "table_management": {
                    "create_table": "Create a new table with specified columns",
                    "list_tables": "List all tables in the database",
                    "get_table_schema": "Get column definitions for a table"
                },
                "crud_operations": {
                    "insert_record": "Insert a new record into a table",
                    "select_records": "Query records from a table with optional WHERE clause",
                    "update_records": "Update records matching a WHERE clause",
                    "delete_records": "Delete records matching a WHERE clause"
                },
                "advanced": {
                    "execute_custom_query": "Execute any custom SQL query"
                }
            },
            "examples": {
                "create_table": 'create_table("users", "id INTEGER PRIMARY KEY, name TEXT, email TEXT")',
                "insert_record": 'insert_record("users", \'{"name": "Alice", "email": "alice@example.com"}\')',
                "select_records": 'select_records("users", "name LIKE \'%Alice%\'", 10)',
                "update_records": 'update_records("users", "email = \'newemail@example.com\'", "id = 1")',
                "delete_records": 'delete_records("users", "id = 1")'
            }
        })
    
    logger.info("Server initialization complete")
    logger.info(f"Custom routes available: /, /health, /docs")
    return mcp

# Made with Bob