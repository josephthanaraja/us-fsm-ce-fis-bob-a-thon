"""
Configuration settings for the File Operations MCP Server.

This module centralizes all configuration values including server metadata,
logging settings, and file operation configuration.
"""

# Server metadata
SERVER_NAME = "FileOperationsServer"
SERVER_VERSION = "1.0.0"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(name)s - %(levelname)s - %(message)s"

# File operation configuration
DEFAULT_ENCODING = "utf-8"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SEARCH_MAX_RESULTS = 1000
ALLOWED_EXTENSIONS = None  # None = all extensions allowed

# Made with Bob