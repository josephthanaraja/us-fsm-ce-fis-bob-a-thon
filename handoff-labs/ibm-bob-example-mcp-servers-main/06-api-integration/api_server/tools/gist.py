"""
GitHub Gist Tool - Demonstrates POST requests.

This module shows how to make POST requests to create resources on an API.

Key Concepts:
- POST requests are used to create new resources
- Request body is sent as JSON
- Authentication via Bearer token in headers
- Proper header configuration (Content-Type, Authorization)
- Response contains the created resource data
"""

import logging
import httpx
from typing import Dict, Any, List, Optional

from ..config import GITHUB_TOKEN, GITHUB_API_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


async def create_gist(
    description: str,
    filename: str,
    content: str,
    public: bool = True
) -> Dict[str, Any]:
    """
    Create a new GitHub Gist using POST request.
    
    This demonstrates a POST request with:
    - JSON request body
    - Bearer token authentication
    - Custom headers (Content-Type, Authorization, User-Agent)
    - Response parsing to extract created resource URL
    
    Args:
        description: Description of the gist
        filename: Name of the file in the gist
        content: Content of the file
        public: Whether the gist should be public (default: True)
        
    Returns:
        Dictionary containing gist information including URL and ID
        
    Raises:
        ValueError: If GitHub token is not configured
        httpx.HTTPError: If the API request fails
    """
    if not GITHUB_TOKEN:
        raise ValueError(
            "GITHUB_TOKEN not configured. "
            "Please set it in your .env file or environment variables. "
            "Get a token at: https://github.com/settings/tokens"
        )
    
    logger.info(f"Creating gist: {description}")
    
    # Prepare the request body
    request_body = {
        "description": description,
        "public": public,
        "files": {
            filename: {
                "content": content
            }
        }
    }
    
    # Prepare headers
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "MCP-API-Integration-Server"
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            # Make POST request with JSON body
            response = await client.post(
                f"{GITHUB_API_URL}/gists",
                json=request_body,
                headers=headers
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            result = {
                "status": "success",
                "gist_id": data["id"],
                "url": data["html_url"],
                "api_url": data["url"],
                "description": data["description"],
                "public": data["public"],
                "created_at": data["created_at"],
                "files": list(data["files"].keys())
            }
            
            logger.info(f"Successfully created gist: {data['html_url']}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating gist: {e.response.status_code}")
            error_data = e.response.json() if e.response.text else {}
            return {
                "status": "error",
                "message": error_data.get("message", "Failed to create gist"),
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error creating gist: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def create_multi_file_gist(
    description: str,
    files: List[Dict[str, str]],
    public: bool = True
) -> Dict[str, Any]:
    """
    Create a gist with multiple files.
    
    This demonstrates a more complex POST request with multiple files.
    
    Args:
        description: Description of the gist
        files: List of dicts with 'filename' and 'content' keys
        public: Whether the gist should be public
        
    Returns:
        Dictionary containing gist information
        
    Example:
        files = [
            {"filename": "hello.py", "content": "print('Hello')"},
            {"filename": "world.js", "content": "console.log('World')"}
        ]
    """
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not configured")
    
    logger.info(f"Creating multi-file gist: {description}")
    
    # Build files object
    files_obj = {}
    for file in files:
        files_obj[file["filename"]] = {
            "content": file["content"]
        }
    
    request_body = {
        "description": description,
        "public": public,
        "files": files_obj
    }
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "MCP-API-Integration-Server"
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{GITHUB_API_URL}/gists",
                json=request_body,
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            result = {
                "status": "success",
                "gist_id": data["id"],
                "url": data["html_url"],
                "description": data["description"],
                "file_count": len(data["files"]),
                "files": list(data["files"].keys()),
                "created_at": data["created_at"]
            }
            
            logger.info(f"Successfully created multi-file gist with {len(files)} files")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating gist: {e.response.status_code}")
            error_data = e.response.json() if e.response.text else {}
            return {
                "status": "error",
                "message": error_data.get("message", "Failed to create gist"),
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error creating gist: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }

# Made with Bob
