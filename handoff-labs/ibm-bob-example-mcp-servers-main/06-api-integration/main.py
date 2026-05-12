import sys
import logging
import argparse
from api_server import create_server

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="API Integration MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport method (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    try:
        logger.info(f"Starting API Integration MCP Server ({args.transport} transport)")
        mcp = create_server()
        
        if args.transport == "stdio":
            mcp.run(transport="stdio", show_banner=False)
        else:
            logger.info(f"Server running on http://127.0.0.1:{args.port}")
            mcp.run(transport="sse", show_banner=False)
        
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
