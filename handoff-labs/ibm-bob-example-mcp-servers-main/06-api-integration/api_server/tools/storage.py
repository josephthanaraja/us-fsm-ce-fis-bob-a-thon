"""
Cloud Storage Tool - Demonstrates DELETE requests.

This module shows how to make DELETE requests to remove resources.

Key Concepts:
- DELETE requests are used to remove resources
- Idempotent operations (deleting same resource twice is safe)
- Authentication via API credentials
- Response typically confirms deletion or returns 404 if already deleted
- Some APIs return 204 No Content on successful deletion
"""

import logging
import httpx
import base64
import hashlib
import time
from typing import Dict, Any

from ..config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_BASE_URL,
    REQUEST_TIMEOUT
)

logger = logging.getLogger(__name__)


def generate_cloudinary_signature(params: dict, api_secret: str) -> str:
    """
    Generate authentication signature for Cloudinary API.
    
    This demonstrates how some APIs require request signing for authentication.
    """
    # Sort parameters and create signature string
    sorted_params = sorted(params.items())
    signature_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    signature_string += api_secret
    
    # Create SHA-1 hash
    return hashlib.sha1(signature_string.encode()).hexdigest()


async def delete_image(
    public_id: str,
    resource_type: str = "image"
) -> Dict[str, Any]:
    """
    Delete an image from Cloudinary using DELETE request.
    
    This demonstrates a DELETE request with:
    - Authentication via API key and signature
    - Resource identification in URL path
    - Handling of 404 (resource not found) gracefully
    - Confirmation of successful deletion
    
    Args:
        public_id: The public ID of the image to delete
        resource_type: Type of resource (image, video, raw)
        
    Returns:
        Dictionary containing deletion status
        
    Raises:
        ValueError: If Cloudinary credentials are not configured
        httpx.HTTPError: If the API request fails
    """
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        raise ValueError(
            "Cloudinary credentials not configured. "
            "Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, "
            "and CLOUDINARY_API_SECRET in your .env file. "
            "Get credentials at: https://cloudinary.com/console"
        )
    
    logger.info(f"Deleting image: {public_id}")
    
    # Prepare authentication
    timestamp = str(int(time.time()))
    params = {
        "public_id": public_id,
        "timestamp": timestamp
    }
    
    signature = generate_cloudinary_signature(params, CLOUDINARY_API_SECRET)
    
    # Prepare request data
    data = {
        **params,
        "api_key": CLOUDINARY_API_KEY,
        "signature": signature
    }
    
    url = f"{CLOUDINARY_BASE_URL}/{CLOUDINARY_CLOUD_NAME}/{resource_type}/destroy"
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            # Make DELETE request (Cloudinary uses POST for destroy endpoint)
            # Note: Some APIs use DELETE method, others use POST to a /destroy endpoint
            response = await client.post(url, data=data)
            
            response.raise_for_status()
            result_data = response.json()
            
            if result_data.get("result") == "ok":
                result = {
                    "status": "success",
                    "message": f"Successfully deleted {public_id}",
                    "public_id": public_id,
                    "resource_type": resource_type
                }
                logger.info(f"Successfully deleted image: {public_id}")
            elif result_data.get("result") == "not found":
                result = {
                    "status": "not_found",
                    "message": f"Image {public_id} not found (may already be deleted)",
                    "public_id": public_id
                }
                logger.warning(f"Image not found: {public_id}")
            else:
                result = {
                    "status": "error",
                    "message": f"Unexpected result: {result_data.get('result')}",
                    "public_id": public_id
                }
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error deleting image: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to delete image: {e.response.text}",
                "status_code": e.response.status_code,
                "public_id": public_id
            }
        except httpx.RequestError as e:
            logger.error(f"Network error deleting image: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}",
                "public_id": public_id
            }


async def delete_multiple_images(
    public_ids: list[str],
    resource_type: str = "image"
) -> Dict[str, Any]:
    """
    Delete multiple images in a batch operation.
    
    This demonstrates batch deletion, which is more efficient than
    deleting items one by one.
    
    Args:
        public_ids: List of public IDs to delete
        resource_type: Type of resource
        
    Returns:
        Dictionary containing batch deletion results
    """
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        raise ValueError("Cloudinary credentials not configured")
    
    logger.info(f"Deleting {len(public_ids)} images in batch")
    
    timestamp = str(int(time.time()))
    params = {
        "public_ids": public_ids,
        "timestamp": timestamp
    }
    
    signature = generate_cloudinary_signature(params, CLOUDINARY_API_SECRET)
    
    data = {
        "public_ids": public_ids,
        "timestamp": timestamp,
        "api_key": CLOUDINARY_API_KEY,
        "signature": signature
    }
    
    url = f"{CLOUDINARY_BASE_URL}/{CLOUDINARY_CLOUD_NAME}/{resource_type}/delete_resources"
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            result_data = response.json()
            
            deleted = result_data.get("deleted", {})
            not_found = result_data.get("not_found", {})
            
            result = {
                "status": "success",
                "deleted_count": len([v for v in deleted.values() if v == "deleted"]),
                "not_found_count": len(not_found),
                "deleted": list(deleted.keys()),
                "not_found": list(not_found.keys())
            }
            
            logger.info(f"Batch deletion complete: {result['deleted_count']} deleted, {result['not_found_count']} not found")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in batch deletion: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to delete images: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error in batch deletion: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def delete_by_prefix(
    prefix: str,
    resource_type: str = "image"
) -> Dict[str, Any]:
    """
    Delete all resources with a specific prefix.
    
    This demonstrates deletion by pattern/filter rather than specific IDs.
    Useful for cleaning up temporary files or test data.
    
    Args:
        prefix: The prefix to match (e.g., "temp/", "test_")
        resource_type: Type of resource
        
    Returns:
        Dictionary containing deletion results
    """
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        raise ValueError("Cloudinary credentials not configured")
    
    logger.info(f"Deleting all images with prefix: {prefix}")
    
    timestamp = str(int(time.time()))
    params = {
        "prefix": prefix,
        "timestamp": timestamp
    }
    
    signature = generate_cloudinary_signature(params, CLOUDINARY_API_SECRET)
    
    data = {
        **params,
        "api_key": CLOUDINARY_API_KEY,
        "signature": signature
    }
    
    url = f"{CLOUDINARY_BASE_URL}/{CLOUDINARY_CLOUD_NAME}/{resource_type}/delete_resources_by_prefix"
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(url, data=data)
            response.raise_for_status()
            result_data = response.json()
            
            result = {
                "status": "success",
                "message": f"Deleted all resources with prefix: {prefix}",
                "prefix": prefix,
                "deleted_counts": result_data.get("deleted", {})
            }
            
            logger.info(f"Successfully deleted resources with prefix: {prefix}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error deleting by prefix: {e.response.status_code}")
            return {
                "status": "error",
                "message": f"Failed to delete by prefix: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            logger.error(f"Network error deleting by prefix: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }

# Made with Bob
