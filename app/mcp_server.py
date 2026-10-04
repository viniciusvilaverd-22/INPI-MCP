from .mcp_adapter import search_trademarks, compare_trademarks, get_trademark_process

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit("SDK MCP ausente. Instale com: pip install '.[mcp]'") from exc

mcp = FastMCP('inpi-trademark-intelligence')

@mcp.tool()
def search_trademark(query: str, nice_classes: list[int] | None = None, limit: int = 20):
    return search_trademarks(query, nice_classes, limit)

@mcp.tool()
def compare_trademark(left_name: str, right_name: str, left_classes: list[int] | None = None, right_classes: list[int] | None = None):
    return compare_trademarks(left_name, right_name, left_classes, right_classes)

@mcp.tool()
def get_trademark(process_number: str):
    return get_trademark_process(process_number)

if __name__ == '__main__':
    mcp.run()
