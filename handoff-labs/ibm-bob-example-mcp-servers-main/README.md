# Example MCP Servers with IBM Bob

Production-ready Model Context Protocol (MCP) server implementations demonstrating progressive complexity levels and real-world integration patterns.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
  - Check your version: `python --version` or `python3 --version`
  - On macOS/Linux, you may need to use `python3` instead of `python`
- **pip** (Python package installer) - Usually comes with Python
  - Check if installed: `pip --version` or `pip3 --version`

### Optional (for specific examples)
- **Podman** - Required for Lab 07 (Code Sandbox)
  - [Podman Installation Guide](https://podman.io/getting-started/installation)
  - Podman is a daemonless container engine for developing, managing, and running containers

## Overview

Eight examples showcasing MCP server development with [FastMCP](https://github.com/jlowin/fastmcp):

| Example | Level | Focus | Transport | Deployment |
|---------|-------|-------|-----------|------------|
| [01-simple-calculator](./01-simple-calculator/) | Beginner | Single-file implementation, core concepts | stdio | Local |
| [02-structured-calculator](./02-structured-calculator/) | Intermediate | Package architecture, production patterns | stdio | Local |
| [03-file-operations](./03-file-operations/) | Intermediate | File system operations, security controls | stdio | Local |
| [04-web-scraping](./04-web-scraping/) | Intermediate | HTML parsing, content extraction, CSS selectors | stdio | Local |
| [05-database-operations](./05-database-operations/) | Intermediate | SQLite CRUD operations, schema management | stdio | Local |
| [06-api-integration](./06-api-integration/) | Advanced | External APIs, HTTP methods, authentication | stdio | Local |
| [07-code-sandbox](./07-code-sandbox/) | Advanced | Containerized code execution, security isolation | Streamable HTTP | Containerized |


## Repository Structure

```
example-mcp-servers/
├── 01-simple-calculator/      # Minimal single-file server
├── 02-structured-calculator/  # Modular package structure
├── 03-file-operations/        # File system operations
├── 04-web-scraping/           # Web content extraction
├── 05-database-operations/    # SQLite database management
├── 06-api-integration/        # Real-world API patterns
└── 07-code-sandbox/           # Containerized code execution (Docker/Podman)
```

### Configuration Tips

- **Local vs Global**: Use `.bob/mcp.json` for project-specific servers, or configure globally in Bob's settings
- **Virtual Environments**: The `command` should point to the Python executable inside each lab's virtual environment
- **Windows Users**: Use Windows path format (e.g., `C:\\path\\to\\venv\\Scripts\\python.exe`)
- **Lab 07**: Require Podman and have different configuration patterns (see their READMEs)

## Key Features

- **Progressive Complexity**: Start simple, scale to production
- **Best Practices**: Type hints, error handling, logging
- **Clear Documentation**: Focused on implementation details

## Requirements

- Python 3.8+
- pip

## Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## License

MIT
