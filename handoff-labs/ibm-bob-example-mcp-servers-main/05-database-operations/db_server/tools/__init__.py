"""
Tools module for the Database Operations MCP Server.

This module exports the tool registration function.
"""

from .database import create_database_tools

def register_all_tools(mcp, db_path: str):
    """
    Register all database tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        db_path: Path to the SQLite database file
    """
    create_database_tools(mcp, db_path)

# Made with Bob