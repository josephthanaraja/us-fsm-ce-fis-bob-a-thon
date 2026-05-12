"""
Trello API Tool - Demonstrates PUT requests.

This module shows how to make PUT requests to update existing resources.

Key Concepts:
- PUT requests are used to update existing resources
- Authentication via API key and token in query parameters
- Partial updates (only send fields that need to change)
- Idempotent operations (same request can be repeated safely)
"""

import logging
import httpx
from typing import Dict, Any, Optional

from ..config import (
    TRELLO_API_KEY,
    TRELLO_TOKEN,
    TRELLO_BASE_URL,
    REQUEST_TIMEOUT
)

logger = logging.getLogger(__name__)


async def update_card(
    card_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    closed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update a Trello card using PUT request.
    
    This demonstrates a PUT request with:
    - Query parameter authentication (API key + token)
    - Partial updates (only specified fields are updated)
    - Optional parameters
    - Resource identification via ID in URL path
    
    Args:
        card_id: The ID of the card to update
        name: New name for the card (optional)
        description: New description (optional)
        due_date: New due date in ISO format (optional)
        closed: Whether to archive the card (optional)
        
    Returns:
        Dictionary containing updated card information
        
    Raises:
        ValueError: If Trello credentials are not configured
        httpx.HTTPError: If the API request fails
    """
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        raise ValueError(
            "TRELLO_API_KEY and TRELLO_TOKEN not configured. "
            "Please set them in your .env file. "
            "Get credentials at: https://trello.com/app-key"
        )
    
    logger.info(f"Updating Trello card: {card_id}")
    
    # Build query parameters for authentication
    auth_params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    # Build update parameters (only include non-None values)
    update_params = {}
    if name is not None:
        update_params["name"] = name
    if description is not None:
        update_params["desc"] = description
    if due_date is not None:
        update_params["due"] = due_date
    if closed is not None:
        update_params["closed"] = closed
    
    # Combine auth and update parameters
    params = {**auth_params, **update_params}
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            # Make PUT request
            response = await client.put(
                f"{TRELLO_BASE_URL}/cards/{card_id}",
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            result = {
                "status": "success",
                "card_id": data["id"],
                "name": data["name"],
                "description": data.get("desc", ""),
                "url": data["url"],
                "due_date": data.get("due"),
                "closed": data["closed"],
                "last_updated": data["dateLastActivity"]
            }
            
            logger.info(f"Successfully updated card: {card_id}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error updating card: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to update card: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error updating card: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def move_card_to_list(
    card_id: str,
    list_id: str
) -> Dict[str, Any]:
    """
    Move a card to a different list using PUT request.
    
    This demonstrates updating a relationship between resources.
    
    Args:
        card_id: The ID of the card to move
        list_id: The ID of the destination list
        
    Returns:
        Dictionary containing updated card information
    """
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        raise ValueError("TRELLO_API_KEY and TRELLO_TOKEN not configured")
    
    logger.info(f"Moving card {card_id} to list {list_id}")
    
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.put(
                f"{TRELLO_BASE_URL}/cards/{card_id}",
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            result = {
                "status": "success",
                "card_id": data["id"],
                "name": data["name"],
                "list_id": data["idList"],
                "board_id": data["idBoard"],
                "url": data["url"]
            }
            
            logger.info(f"Successfully moved card to list: {list_id}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error moving card: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to move card: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error moving card: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def update_card_labels(
    card_id: str,
    label_ids: list[str]
) -> Dict[str, Any]:
    """
    Update the labels on a card.
    
    This demonstrates updating a collection/array field.
    
    Args:
        card_id: The ID of the card
        label_ids: List of label IDs to set on the card
        
    Returns:
        Dictionary containing updated card information
    """
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        raise ValueError("TRELLO_API_KEY and TRELLO_TOKEN not configured")
    
    logger.info(f"Updating labels for card: {card_id}")
    
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idLabels": ",".join(label_ids)  # Comma-separated list
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.put(
                f"{TRELLO_BASE_URL}/cards/{card_id}",
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            result = {
                "status": "success",
                "card_id": data["id"],
                "name": data["name"],
                "labels": [
                    {"id": label["id"], "name": label["name"], "color": label["color"]}
                    for label in data.get("labels", [])
                ]
            }
            
            logger.info(f"Successfully updated labels for card: {card_id}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error updating labels: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to update labels: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error updating labels: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }

async def search_cards(
    board_id: str,
    query: str
) -> Dict[str, Any]:
    """
    Search for cards on a Trello board by name.
    
    Args:
        board_id: The ID of the board to search
        query: Search query (card name to search for)
        
    Returns:
        Dictionary containing matching cards
    """
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        raise ValueError("TRELLO_API_KEY and TRELLO_TOKEN not configured")
    
    logger.info(f"Searching for cards matching '{query}' on board {board_id}")
    
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            # Get all cards on the board
            response = await client.get(
                f"{TRELLO_BASE_URL}/boards/{board_id}/cards",
                params=params
            )
            
            response.raise_for_status()
            cards = response.json()
            
            # Filter cards by name (case-insensitive)
            matching_cards = [
                {
                    "id": card["id"],
                    "name": card["name"],
                    "list_id": card["idList"],
                    "url": card["url"],
                    "description": card.get("desc", "")
                }
                for card in cards
                if query.lower() in card["name"].lower()
            ]
            
            result = {
                "status": "success",
                "query": query,
                "matches": len(matching_cards),
                "cards": matching_cards
            }
            
            logger.info(f"Found {len(matching_cards)} matching cards")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching cards: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to search cards: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error searching cards: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def get_board_lists(
    board_id: str
) -> Dict[str, Any]:
    """
    Get all lists on a Trello board.
    
    Args:
        board_id: The ID of the board
        
    Returns:
        Dictionary containing all lists on the board
    """
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        raise ValueError("TRELLO_API_KEY and TRELLO_TOKEN not configured")
    
    logger.info(f"Getting lists for board {board_id}")
    
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.get(
                f"{TRELLO_BASE_URL}/boards/{board_id}/lists",
                params=params
            )
            
            response.raise_for_status()
            lists = response.json()
            
            result = {
                "status": "success",
                "board_id": board_id,
                "lists": [
                    {
                        "id": lst["id"],
                        "name": lst["name"],
                        "closed": lst.get("closed", False)
                    }
                    for lst in lists
                ]
            }
            
            logger.info(f"Found {len(lists)} lists on board")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting lists: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to get lists: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error getting lists: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }

# Made with Bob
