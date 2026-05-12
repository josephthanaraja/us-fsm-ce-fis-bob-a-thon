"""
Entry point for the Web Scraping MCP Server.

This script creates and runs the server using the factory pattern.
"""

import logging
import sys
import os
from scraper_server import create_server

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("web-scraping-mcp-server")


def main():
    """Main entry point for the server."""
    # Get configuration from environment or use defaults
    timeout = int(os.getenv("SCRAPER_TIMEOUT", "30"))
    user_agent = os.getenv("SCRAPER_USER_AGENT", 
                          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    logger.info(f"Starting Web Scraping MCP Server...")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"User-Agent: {user_agent[:50]}...")
    
    try:
        # Create the server using the factory function
        mcp = create_server(timeout, user_agent)
        
        # Run the server with SSE transport
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