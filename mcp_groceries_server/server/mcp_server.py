from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from mcp_groceries_server.server.providers.shufersal._service import close_browser

@asynccontextmanager
async def lifespan(app: FastMCP):
    # Startup
    yield
    # Shutdown
    await close_browser()

server = FastMCP("Groceries", lifespan=lifespan)
