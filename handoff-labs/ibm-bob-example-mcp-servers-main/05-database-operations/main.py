"""
Entry point for the Database Operations MCP Server.

This script creates and runs the server using the factory pattern.
"""

import logging
import sys
import os
from db_server import create_server

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("database-mcp-server")


def main():
    """Main entry point for the server."""
    # Get database path from environment or use default
    db_path = os.getenv("DB_PATH", "example.db")
    
    # Make database path absolute if relative
    if not os.path.isabs(db_path):
        # Get the directory where main.py is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, db_path)
    
    logger.info(f"Starting Database Operations MCP Server...")
    logger.info(f"Database: {db_path}")
    
    try:
        # Create the server using the factory function
        mcp = create_server(db_path)
        
        # Run the server with stdio transport (for Bob/MCP clients)
        # Disable banner to avoid cluttering Bob's logs
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