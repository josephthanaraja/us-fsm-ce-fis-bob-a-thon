"""
Tools module for the Code Execution Sandbox MCP Server.

This module exports the tool registration function.
"""

from .executor import create_executor_tools

def register_all_tools(mcp, timeout: int, max_output_size: int):
    """
    Register all code execution tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        timeout: Execution timeout in seconds
        max_output_size: Maximum output size in bytes
    """
    create_executor_tools(mcp, timeout, max_output_size)

# Made with Bob