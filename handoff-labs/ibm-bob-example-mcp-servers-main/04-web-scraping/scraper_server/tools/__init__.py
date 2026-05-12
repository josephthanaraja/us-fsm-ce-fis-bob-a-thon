"""
Tools module for the Web Scraping MCP Server.

This module exports the tool registration function.
"""

from .scraper import create_scraper_tools

def register_all_tools(mcp, timeout: int, user_agent: str):
    """
    Register all web scraping tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        timeout: Request timeout in seconds
        user_agent: User agent string for HTTP requests
    """
    create_scraper_tools(mcp, timeout, user_agent)

# Made with Bob