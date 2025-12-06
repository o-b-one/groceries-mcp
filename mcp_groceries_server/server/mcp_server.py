from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from mcp_groceries_server.server.providers.shufersal._service import close_browser

server = FastMCP("Groceries", host="0.0.0.0")
