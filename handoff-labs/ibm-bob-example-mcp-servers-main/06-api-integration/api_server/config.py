"""
Configuration module for the API Integration MCP Server.

This module centralizes all configuration constants, making it easy to modify
settings without touching the core logic.

Key Concepts:
- Centralized configuration improves maintainability
- Constants are in UPPER_CASE by convention
- Environment variables allow different configs per deployment
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Server Configuration
SERVER_NAME = "APIIntegrationServer"
SERVER_VERSION = "1.0.0"
DEFAULT_PORT = 8000

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(name)s - %(levelname)s - %(message)s"

# API Configuration - Load from environment variables
# These should be set in a .env file or environment
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY", "")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN", "")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# API Endpoints
WEATHERAPI_BASE_URL = "https://api.weatherapi.com/v1"
GITHUB_API_URL = "https://github.ibm.com/api/v3"
GITHUB_GRAPHQL_URL = "https://github.ibm.com/api/graphql"
TRELLO_BASE_URL = "https://api.trello.com/1"
CLOUDINARY_BASE_URL = "https://api.cloudinary.com/v1_1"

# Request Configuration
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3

# Made with Bob
