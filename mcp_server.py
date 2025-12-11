from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Surelook Holmes")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers. A simple test tool."""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a greeting for a name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Run the server with SSE transport (streamable-http)
    # This will typically start a uvicorn server
    print("Starting Surelook Holmes MCP server on SSE transport...")
    mcp.run(transport="sse")
