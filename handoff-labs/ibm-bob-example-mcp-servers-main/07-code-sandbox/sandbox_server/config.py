"""
Configuration settings for the Code Execution Sandbox MCP Server.

This module centralizes all configuration values including server metadata,
logging settings, and execution limits.
"""

# Server metadata
SERVER_NAME = "CodeSandboxServer"
SERVER_VERSION = "1.0.0"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(name)s - %(levelname)s - %(message)s"

# Execution limits
DEFAULT_TIMEOUT = 30  # seconds
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB
MEMORY_LIMIT = "256m"  # Docker memory limit
CPU_LIMIT = "1.0"  # Docker CPU limit

# Supported languages
SUPPORTED_LANGUAGES = ["python", "javascript", "bash"]

# Made with Bob