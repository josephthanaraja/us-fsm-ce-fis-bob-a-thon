"""
Configuration settings for the Web Scraping MCP Server.

This module centralizes all configuration values including server metadata,
logging settings, and scraping configuration.
"""

# Server metadata
SERVER_NAME = "WebScrapingServer"
SERVER_VERSION = "1.0.0"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(name)s - %(levelname)s - %(message)s"

# Scraping configuration
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
MAX_RETRIES = 3

# Made with Bob