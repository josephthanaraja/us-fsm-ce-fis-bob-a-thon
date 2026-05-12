"""
Weather API Tool - Demonstrates GET requests using WeatherAPI.com.

This module shows how to make GET requests to WeatherAPI.com with query parameters.

Key Concepts:
- GET requests are used to retrieve data
- Query parameters are passed via the params argument
- API keys are typically passed as query parameters or headers
- Error handling for network failures and API errors
- Async/await for non-blocking I/O
"""

import logging
import httpx
from typing import Dict, Any

from ..config import WEATHERAPI_KEY, WEATHERAPI_BASE_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


async def get_weather(city: str) -> Dict[str, Any]:
    """
    Fetch current weather data for a city using WeatherAPI.com.
    
    This demonstrates a GET request with:
    - Query parameters (city, API key)
    - Error handling for missing API keys
    - HTTP status code checking
    - JSON response parsing
    
    Args:
        city: Name of the city to get weather for
        
    Returns:
        Dictionary containing weather data including temperature, description, etc.
        
    Raises:
        ValueError: If API key is not configured
        httpx.HTTPError: If the API request fails
    """
    if not WEATHERAPI_KEY:
        raise ValueError(
            "WEATHERAPI_KEY not configured. "
            "Please set it in your .env file or environment variables. "
            "Get a free API key at: https://www.weatherapi.com/signup.aspx"
        )
    
    logger.info(f"Fetching weather data for city: {city}")
    
    # Create an async HTTP client
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            # Make GET request with query parameters
            response = await client.get(
                f"{WEATHERAPI_BASE_URL}/current.json",
                params={
                    "key": WEATHERAPI_KEY,
                    "q": city,
                    "aqi": "no"  # Don't include air quality data
                }
            )
            
            # Raise an exception for 4xx/5xx status codes
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract and format the relevant information
            result = {
                "city": data["location"]["name"],
                "region": data["location"]["region"],
                "country": data["location"]["country"],
                "temperature_c": data["current"]["temp_c"],
                "temperature_f": data["current"]["temp_f"],
                "feels_like_c": data["current"]["feelslike_c"],
                "feels_like_f": data["current"]["feelslike_f"],
                "humidity": data["current"]["humidity"],
                "condition": data["current"]["condition"]["text"],
                "wind_mph": data["current"]["wind_mph"],
                "wind_kph": data["current"]["wind_kph"],
                "last_updated": data["current"]["last_updated"],
                "status": "success"
            }
            
            logger.info(f"Successfully fetched weather for {city}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching weather: {e.response.status_code}")
            if e.response.status_code == 400:
                return {
                    "status": "error",
                    "message": f"City '{city}' not found or invalid"
                }
            elif e.response.status_code == 401:
                return {
                    "status": "error",
                    "message": "Invalid API key. Please check your WEATHERAPI_KEY in .env file"
                }
            elif e.response.status_code == 403:
                return {
                    "status": "error",
                    "message": "API key quota exceeded or access denied"
                }
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error fetching weather: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }


async def get_forecast(city: str, days: int = 5) -> Dict[str, Any]:
    """
    Fetch weather forecast for a city using WeatherAPI.com.
    
    This demonstrates another GET request pattern with different parameters.
    
    Args:
        city: Name of the city
        days: Number of days to forecast (1-10 for free tier, 1-14 for paid)
        
    Returns:
        Dictionary containing forecast data
    """
    if not WEATHERAPI_KEY:
        raise ValueError(
            "WEATHERAPI_KEY not configured. "
            "Get a free API key at: https://www.weatherapi.com/signup.aspx"
        )
    
    # Limit days to 3 for free tier
    if days > 3:
        days = 3
        logger.warning(f"Free tier limited to 3 days forecast, adjusting from {days}")
    
    logger.info(f"Fetching {days}-day forecast for city: {city}")
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.get(
                f"{WEATHERAPI_BASE_URL}/forecast.json",
                params={
                    "key": WEATHERAPI_KEY,
                    "q": city,
                    "days": days,
                    "aqi": "no",
                    "alerts": "no"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Simplify the forecast data
            forecasts = []
            for day in data["forecast"]["forecastday"]:
                forecasts.append({
                    "date": day["date"],
                    "max_temp_c": day["day"]["maxtemp_c"],
                    "max_temp_f": day["day"]["maxtemp_f"],
                    "min_temp_c": day["day"]["mintemp_c"],
                    "min_temp_f": day["day"]["mintemp_f"],
                    "avg_temp_c": day["day"]["avgtemp_c"],
                    "avg_temp_f": day["day"]["avgtemp_f"],
                    "condition": day["day"]["condition"]["text"],
                    "chance_of_rain": day["day"]["daily_chance_of_rain"],
                    "chance_of_snow": day["day"]["daily_chance_of_snow"]
                })
            
            result = {
                "city": data["location"]["name"],
                "region": data["location"]["region"],
                "country": data["location"]["country"],
                "forecasts": forecasts,
                "status": "success"
            }
            
            logger.info(f"Successfully fetched forecast for {city}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching forecast: {e.response.status_code}")
            if e.response.status_code == 400:
                return {
                    "status": "error",
                    "message": f"City '{city}' not found or invalid"
                }
            elif e.response.status_code == 401:
                return {
                    "status": "error",
                    "message": "Invalid API key. Please check your WEATHERAPI_KEY in .env file"
                }
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error fetching forecast: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }

# Made with Bob
