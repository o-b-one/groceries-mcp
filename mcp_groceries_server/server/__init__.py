import argparse
import enum
import os

from mcp_groceries_server.server.prompts import shopping_prompts

from .mcp_server import server


class Vendors(enum.Enum):
    RamiLevy = "rami-levy"
    Keshet = "keshet"


def main():
    parser = argparse.ArgumentParser(description="Groceries MCP Server")
    parser.add_argument("--vendor", help="The vendor to work against")
    args = parser.parse_args()
    vendor = args.vendor or os.environ.get("VENDOR")
    if vendor == Vendors.RamiLevy.value:
        from mcp_groceries_server.server.providers.rami_levy.tools import RamiLevyProvider  # pylint: disable=import-outside-toplevel

        RamiLevyProvider()
    elif vendor == Vendors.Keshet.value:
        from mcp_groceries_server.server.providers.keshet.tools import KeshetProvider  # pylint: disable=import-outside-toplevel

        KeshetProvider()
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")

    server.run(transport="stdio")
