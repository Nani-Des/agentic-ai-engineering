"""
A small MCP server that exposes the course's telco and mobile-money tools.

Run it on its own to test:      python telco_mcp_server.py
Inspect it in a browser:         npx @modelcontextprotocol/inspector python telco_mcp_server.py
Any MCP client (Lab 3, Claude Desktop, Cursor, VS Code) can then use these tools without new code.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.fastmcp import FastMCP

from common import tools as T

mcp = FastMCP("ghana-telco-tools")


@mcp.tool()
def get_momo_balance(phone: str) -> dict:
    """Get the mobile-money wallet balance in GHS for a 10-digit Ghana phone number."""
    return T.get_momo_balance(phone)


@mcp.tool()
def list_data_bundles(network: str) -> dict:
    """List data bundles and prices in GHS for a network: MTN, Telecel or AT."""
    return T.list_data_bundles(network)


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert money between GHS, USD, EUR, GBP, NGN and XOF (demo rates)."""
    return T.convert_currency(amount, from_currency, to_currency)


@mcp.resource("faq://all")
def faq() -> str:
    """The full customer FAQ, as a readable resource."""
    return "\n".join(f"- {k}: {v}" for k, v in T.KNOWLEDGE_BASE.items())


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
