"""
API Integration MCP Server Package.

This package provides an MCP server that demonstrates various types of
HTTP requests and API integrations.

Key Features:
- GET requests (Weather API)
- POST requests (GitHub Gists)
- PUT requests (Trello)
- DELETE requests (Cloudinary)
- GraphQL queries (GitHub)

Usage:
    from api_server import create_server
    
    mcp = create_server()
    mcp.run(transport="stdio")
"""

from .server import create_server

__version__ = "1.0.0"
__all__ = ["create_server"]

# Made with Bob
