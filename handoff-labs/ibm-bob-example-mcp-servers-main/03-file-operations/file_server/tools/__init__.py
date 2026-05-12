"""
Tools module for the File Operations MCP Server.

This module exports the tool registration function.
"""

from .file_ops import create_file_tools

def register_all_tools(mcp, base_path: str, encoding: str, max_file_size: int):
    """
    Register all file operation tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        base_path: Base directory for file operations
        encoding: Default file encoding
        max_file_size: Maximum file size in bytes
    """
    create_file_tools(mcp, base_path, encoding, max_file_size)

# Made with Bob