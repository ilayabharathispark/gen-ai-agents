from fastmcp import FastMCP

mcp = FastMCP("My Basic MCP Server")

@mcp.tool
def add_numbers(a: float, b: float) -> float:
    return a + b

@mcp.tool
def reverse_string(text: str) -> str:
    """Reverse a given string."""
    return text[::-1]

@mcp.tool
def murugan_details(text: str) -> str:
    """Get details about Murugan."""
    return "Murugan is a ilaya's father."

@mcp.resource("info://about")
def about_server():
    return "This is a basic MCP server."

if __name__ == "__main__":
    mcp.run()