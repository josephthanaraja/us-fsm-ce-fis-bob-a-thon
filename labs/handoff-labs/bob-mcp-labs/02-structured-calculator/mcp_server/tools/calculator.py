import logging

logger = logging.getLogger(__name__)

def register_calculator_tools(mcp):
    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Add two numbers together and return the sum."""
        logger.info(f"Tool called: add({a}, {b})")
        return a + b
    
    @mcp.tool()
    def subtract(a: int, b: int) -> int:
        """Subtract b from a and return the difference."""
        logger.info(f"Tool called: subtract({a}, {b})")
        return a - b
    
    @mcp.tool()
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers and return the product."""
        logger.info(f"Tool called: multiply({a}, {b})")
        return a * b
    
    @mcp.tool()
    def divide(a: float, b: float) -> float:
        """Divide a by b and return the quotient."""
        logger.info(f"Tool called: divide({a}, {b})")
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    logger.info("Calculator tools registered")

# Made with Bob
