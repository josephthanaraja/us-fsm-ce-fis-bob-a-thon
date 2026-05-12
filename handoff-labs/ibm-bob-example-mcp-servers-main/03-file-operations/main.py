"""
Entry point for the File Operations MCP Server.

This script creates and runs the server using the factory pattern.
"""

import logging
import sys
import os
from file_server import create_server

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("file-operations-mcp-server")


def main():
    """Main entry point for the server."""
    # Get configuration from environment or use defaults
    base_path = os.getenv("FILE_BASE_PATH", ".")
    encoding = os.getenv("FILE_ENCODING", "utf-8")
    max_file_size = int(os.getenv("FILE_MAX_SIZE", str(10 * 1024 * 1024)))  # 10MB default
    
    logger.info(f"Starting File Operations MCP Server...")
    logger.info(f"Base path: {os.path.abspath(base_path)}")
    logger.info(f"Encoding: {encoding}")
    logger.info(f"Max file size: {max_file_size} bytes")
    
    try:
        # Create the server using the factory function
        mcp = create_server(base_path, encoding, max_file_size)
        
        # Run the server with stdio transport
        mcp.run(transport="stdio", show_banner=False)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Server terminated")


if __name__ == "__main__":
    main()

# Made with Bob