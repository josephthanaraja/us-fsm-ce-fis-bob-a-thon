from .server import create_server
from .config import SERVER_NAME, SERVER_VERSION

__version__ = SERVER_VERSION
__all__ = ["create_server", "SERVER_NAME", "SERVER_VERSION"]

# Made with Bob
