import argparse
import asyncio
import enum

from mcp_groceries_server.server.prompts import shopping_prompts

from .mcp_server import server


class Vendors(enum.Enum):
    RamiLevy = "rami-levy"


def main():
    parser = argparse.ArgumentParser(description="Groceries MCP Server")
    parser.add_argument("--vendor", help="The vendor to work against")
    args = parser.parse_args()
    vendor = args.vendor
    if vendor == Vendors.RamiLevy.value:
        import mcp_groceries_server.server.providers.rami_levy
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")
    
    server.run(transport="stdio")