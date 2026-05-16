# Structured Calculator MCP Server

Production-ready MCP server with modular package architecture.

## Architecture

```mermaid
graph TD
    A[MCP Client] -->|SSE/stdio| B[main.py]
    B --> C[create_server Factory]
    C --> D[FastMCP Instance]
    D --> E[Tool Registration]
    E --> F[Calculator Tools]
    F --> G[add]
    F --> H[subtract]
    F --> I[multiply]
    F --> J[divide]
    D --> K[Custom Routes]
    K --> L[Root endpoint]
    K --> M[Health endpoint]
    
    N[config.py] -.->|Configuration| C
    
    style B fill:#4CAF50
    style C fill:#2196F3
    style D fill:#FF9800
    style F fill:#9C27B0
```

### Project Structure

```text
02-structured-calculator/
├── main.py              # Entry point
├── mcp_server/
│   ├── __init__.py      # Package exports
│   ├── config.py        # Configuration
│   ├── server.py        # Server factory
│   └── tools/
│       ├── __init__.py  # Tool registration
│       └── calculator.py
```

### Features

- Python package structure
- Separation of concerns
- Factory pattern
- Modular tool registration
- Configuration management
- Health check endpoints

### Available Tools

- `add(a: int, b: int) -> int`
- `subtract(a: int, b: int) -> int`
- `multiply(a: int, b: int) -> int`
- `divide(a: int, b: int) -> float`

## Installation

```bash
cd 02-structured-calculator

# Create virtual environment with uv
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

## Usage

### Configure MCP Server in Bob

1. **Navigate to Bob Settings**
   - Open Bob's settings/preferences

2. **Navigate to MCP Servers**
   - Find the MCP Servers section in settings

3. **Open Configuration File**
   - Click to open the Local (project-specific) configuration file

4. **Add Server Configuration**
   - Add the following configuration to the `.bob/mcp.json` file:

   ```json
   {
     "mcpServers": {
       "structured-calculator": {
         "command": "/absolute/path/to/example-mcp-servers/02-structured-calculator/.venv/bin/python",
         "args": ["/absolute/path/to/example-mcp-servers/02-structured-calculator/main.py"]
       }
     }
   }
   ```

   **For Windows users**, use the Windows path format:

   ```json
   {
     "mcpServers": {
       "structured-calculator": {
         "command": "C:\\absolute\\path\\to\\example-mcp-servers\\02-structured-calculator\\.venv\\Scripts\\python.exe",
         "args": ["C:\\absolute\\path\\to\\example-mcp-servers\\02-structured-calculator\\main.py"]
       }
     }
   }
   ```

   > **Note:** Replace `/absolute/path/to/example-mcp-servers` with the actual path to this repository on your system. The `command` should point to the Python executable inside the virtual environment (`.venv/bin/python` on macOS/Linux or `.venv\Scripts\python.exe` on Windows) to ensure all dependencies are available.

5. **Verify Server Status**
   - Check that the MCP server shows a green indicator light
   - Click on the `structured-calculator` server in Bob's MCP servers list and click the **Restart server** icon.

   > **Note:** If you see import errors for `fastmcp` or `starlette` in your editor, this is normal. The server uses the virtual environment where these packages are installed, so as long as the MCP server indicator light is green, everything is working correctly.

### How to Use This Server

Once configured, switch to **Advanced mode** (or any mode with MCP capabilities) and try:

```text
"Use the structured calculator to multiply 15 by 4"
```

Bob will use the appropriate tool from this MCP server to perform the calculation.

#### Extra Abilities

This server includes additional operations beyond the simple calculator, feel free to test any of the following operations:

- Subtraction
- Multiplication
- Division with error handling for division by zero

### Extending

Explore further by adding new tools:

1. Create tool file in `mcp_server/tools/`
2. Define tools with `@mcp.tool()` decorator
3. Register in `tools/__init__.py`

Configuration changes go in `config.py`.

## Cleanup

When you're done with this lab and want to clean up:

1. Deactivate Virtual Environment

  ```bash
  # Deactivate the virtual environment
  deactivate
  ```

1. Remove MCP Server Configuration

    - Open `.bob/mcp.json` and remove the `structured-calculator` server entry:

1. [Optionally] Remove the virtual environment if you want to free up disk space:

    ```bash
    # From the lab directory
    rm -rf .venv
    ```
