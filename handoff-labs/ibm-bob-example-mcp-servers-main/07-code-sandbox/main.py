"""
Entry point for the Code Execution Sandbox MCP Server.

This script creates and runs the server using the factory pattern.
"""

import logging
import sys
import os
from sandbox_server import create_server

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("code-sandbox-mcp-server")


def main():
    """Main entry point for the server."""
    # Get configuration from environment or use defaults
    timeout = int(os.getenv("SANDBOX_TIMEOUT", "30"))
    max_output_size = int(os.getenv("SANDBOX_MAX_OUTPUT", str(1024 * 1024)))
    
    logger.info(f"Starting Code Execution Sandbox MCP Server...")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"Max output: {max_output_size} bytes")
    logger.info(f"Running in container: {os.path.exists('/.dockerenv')}")
    
    try:
        # Create the server using the factory function
        mcp = create_server(timeout, max_output_size)
        
        port = int(os.getenv("PORT", "8080"))
        host = os.getenv("HOST", "0.0.0.0")  # bind inside container

        mcp.run(
            transport="streamable-http",
            host=host,
            port=port
        )
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