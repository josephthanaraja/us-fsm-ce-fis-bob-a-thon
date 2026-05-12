"""
Code Execution Sandbox MCP Server package.

This package provides a FastMCP server for safe code execution in containers.
"""

from .server import create_server

__all__ = ["create_server"]

# Made with Bob