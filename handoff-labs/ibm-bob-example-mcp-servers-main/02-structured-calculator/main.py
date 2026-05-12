import sys
import logging
from mcp_server import create_server

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting MCP Server...")
        mcp = create_server()
        mcp.run(transport="stdio", show_banner=False)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    main()

# Made with Bob
