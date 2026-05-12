"""
Tools package initialization.

This module registers all MCP tools with the server.

Key Concepts:
- Central registration point for all tools
- Easy to enable/disable tool groups
- Keeps tool organization clean
- Allows for conditional tool loading
"""

import logging
from fastmcp import FastMCP

# Import all tool modules
from . import weather
from . import gist
from . import trello
from . import storage
from . import github_graphql

logger = logging.getLogger(__name__)


def register_all_tools(mcp: FastMCP) -> None:
    """
    Register all API integration tools with the MCP server.
    
    This function:
    1. Registers each tool with the FastMCP server
    2. Logs successful registration
    3. Provides a central place to manage tool availability
    
    Args:
        mcp: The FastMCP server instance to register tools with
    """
    logger.info("Registering API integration tools...")
    
    # Weather Tools (GET requests)
    @mcp.tool()
    async def get_weather(city: str) -> dict:
        """
        Get current weather for a city.
        
        Example: get_weather("London")
        """
        return await weather.get_weather(city)
    
    @mcp.tool()
    async def get_forecast(city: str, days: int = 5) -> dict:
        """
        Get weather forecast for a city.
        
        Args:
            city: Name of the city
            days: Number of days to forecast (1-5)
        
        Example: get_forecast("Paris", 3)
        """
        return await weather.get_forecast(city, days)
    
    # GitHub Gist Tools (POST requests)
    @mcp.tool()
    async def create_gist(
        description: str,
        filename: str,
        content: str,
        public: bool = True
    ) -> dict:
        """
        Create a new GitHub Gist.
        
        Args:
            description: Description of the gist
            filename: Name of the file
            content: Content of the file
            public: Whether the gist should be public
        
        Example: create_gist("My code snippet", "hello.py", "print('Hello')")
        """
        return await gist.create_gist(description, filename, content, public)
    
    @mcp.tool()
    async def create_multi_file_gist(
        description: str,
        files: list,
        public: bool = True
    ) -> dict:
        """
        Create a gist with multiple files.
        
        Args:
            description: Description of the gist
            files: List of dicts with 'filename' and 'content' keys
            public: Whether the gist should be public
        
        Example: create_multi_file_gist(
            "Multi-file example",
            [
                {"filename": "hello.py", "content": "print('Hello')"},
                {"filename": "world.js", "content": "console.log('World')"}
            ]
        )
        """
        return await gist.create_multi_file_gist(description, files, public)
    
    # Trello Tools (PUT requests)
    @mcp.tool()
    async def update_trello_card(
        card_id: str,
        name: str | None = None,
        description: str | None = None,
        due_date: str | None = None,
        closed: bool | None = None
    ) -> dict:
        """
        Update a Trello card.
        
        Args:
            card_id: The ID of the card to update
            name: New name (optional)
            description: New description (optional)
            due_date: New due date in ISO format (optional)
            closed: Whether to archive the card (optional)
        
        Example: update_trello_card("abc123", name="Updated Task", closed=False)
        """
        return await trello.update_card(card_id, name, description, due_date, closed)
    
    @mcp.tool()
    async def move_trello_card(card_id: str, list_id: str) -> dict:
        """
        Move a Trello card to a different list.
        
        Args:
            card_id: The ID of the card to move
            list_id: The ID of the destination list
        
        Example: move_trello_card("abc123", "xyz789")
        """
        return await trello.move_card_to_list(card_id, list_id)
    
    @mcp.tool()
    async def update_trello_card_labels(card_id: str, label_ids: list) -> dict:
        """
        Update the labels on a Trello card.
        
        Args:
            card_id: The ID of the card
            label_ids: List of label IDs to set
        
        Example: update_trello_card_labels("abc123", ["label1", "label2"])
        """
        return await trello.update_card_labels(card_id, label_ids)
    
    @mcp.tool()
    async def search_trello_cards(board_id: str, query: str) -> dict:
        """
        Search for cards on a Trello board by name.
        
        Args:
            board_id: The ID of the board to search
            query: Search query (card name to search for)
        
        Example: search_trello_cards("board123", "Test")
        """
        return await trello.search_cards(board_id, query)
    
    @mcp.tool()
    async def get_trello_board_lists(board_id: str) -> dict:
        """
        Get all lists on a Trello board.
        
        Args:
            board_id: The ID of the board
        
        Example: get_trello_board_lists("board123")
        """
        return await trello.get_board_lists(board_id)
    
    # Cloud Storage Tools (DELETE requests)
    @mcp.tool()
    async def delete_image(public_id: str, resource_type: str = "image") -> dict:
        """
        Delete an image from Cloudinary.
        
        Args:
            public_id: The public ID of the image
            resource_type: Type of resource (image, video, raw)
        
        Example: delete_image("sample_image")
        """
        return await storage.delete_image(public_id, resource_type)
    
    @mcp.tool()
    async def delete_multiple_images(public_ids: list, resource_type: str = "image") -> dict:
        """
        Delete multiple images in a batch.
        
        Args:
            public_ids: List of public IDs to delete
            resource_type: Type of resource
        
        Example: delete_multiple_images(["img1", "img2", "img3"])
        """
        return await storage.delete_multiple_images(public_ids, resource_type)
    
    @mcp.tool()
    async def delete_images_by_prefix(prefix: str, resource_type: str = "image") -> dict:
        """
        Delete all images with a specific prefix.
        
        Args:
            prefix: The prefix to match
            resource_type: Type of resource
        
        Example: delete_images_by_prefix("temp/")
        """
        return await storage.delete_by_prefix(prefix, resource_type)
    
    # GitHub GraphQL Tools
    @mcp.tool()
    async def search_github_repositories(
        query: str,
        limit: int = 10,
        sort: str = "STARS"
    ) -> dict:
        """
        Search GitHub repositories using GraphQL.
        
        Args:
            query: Search query (e.g., "language:python stars:>1000")
            limit: Maximum number of results
            sort: Sort order (STARS, FORKS, UPDATED)
        
        Example: search_github_repositories("language:python stars:>1000", 5)
        """
        return await github_graphql.search_repositories(query, limit, sort)
    
    @mcp.tool()
    async def get_github_user_profile(username: str, include_repos: bool = True) -> dict:
        """
        Get a GitHub user's profile.
        
        Args:
            username: GitHub username
            include_repos: Whether to include user's repositories
        
        Example: get_github_user_profile("torvalds")
        """
        return await github_graphql.get_user_profile(username, include_repos)
    
    @mcp.tool()
    async def get_github_repository_issues(
        owner: str,
        repo: str,
        state: str = "OPEN",
        limit: int = 10
    ) -> dict:
        """
        Get issues for a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (OPEN, CLOSED)
            limit: Maximum number of issues
        
        Example: get_github_repository_issues("facebook", "react", "OPEN", 5)
        """
        return await github_graphql.get_repository_issues(owner, repo, state, limit)
    
    logger.info("Successfully registered all API integration tools")
    logger.info("Available tools:")
    logger.info("  Weather: get_weather, get_forecast")
    logger.info("  GitHub Gists: create_gist, create_multi_file_gist")
    logger.info("  Trello: update_trello_card, move_trello_card, update_trello_card_labels, search_trello_cards, get_trello_board_lists")
    logger.info("  Cloud Storage: delete_image, delete_multiple_images, delete_images_by_prefix")
    logger.info("  GitHub GraphQL: search_github_repositories, get_github_user_profile, get_github_repository_issues")

# Made with Bob
