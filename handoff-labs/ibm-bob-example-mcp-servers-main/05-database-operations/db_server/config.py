"""
Configuration settings for the Database Operations MCP Server.

This module centralizes all configuration values including server metadata,
logging settings, and database configuration.
"""

# Server metadata
SERVER_NAME = "DatabaseOperationsServer"
SERVER_VERSION = "1.0.0"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(name)s - %(levelname)s - %(message)s"

# Database configuration
DEFAULT_DB_PATH = "example.db"
MAX_QUERY_RESULTS = 1000

# Made with Bob