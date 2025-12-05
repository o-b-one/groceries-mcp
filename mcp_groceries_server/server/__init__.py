import argparse
import enum
import os

from mcp_groceries_server.server.prompts import shopping_prompts

from mcp_groceries_server.server.mcp_server import server


class Vendors(enum.Enum):
    RamiLevy = "rami-levy"
    Keshet = "keshet"
    Shufersal = "shufersal"


def main():
    parser = argparse.ArgumentParser(description="Groceries MCP Server")
    parser.add_argument("--vendor", help="The vendor to work against", default="")
    parser.add_argument("--transport", help="the mcp transport protocol", choices=["streamable-http", "stdio", "sse"], default="streamable-http")
    
    args = parser.parse_args()
    
    vendor = args.vendor or os.environ.get("VENDOR")
    transport = args.transport
    match vendor:
        case Vendors.RamiLevy.value:
            from mcp_groceries_server.server.providers.rami_levy.tools import RamiLevyProvider  # pylint: disable=import-outside-toplevel
            RamiLevyProvider()
        case Vendors.Keshet.value:
            from mcp_groceries_server.server.providers.keshet.tools import KeshetProvider  # pylint: disable=import-outside-toplevel
            KeshetProvider()
        case Vendors.Shufersal.value:
            from mcp_groceries_server.server.providers.shufersal.tools import ShufersalProvider  # pylint: disable=import-outside-toplevel
            ShufersalProvider()
        case _:
            raise ValueError(f"Unsupported vendor: {vendor}")
    
    server.run(transport=transport)
    # server.run(transport="stdio")



if __name__ == "__main__":
    from mcp_groceries_server.server.providers.shufersal.tools import ShufersalProvider  # pylint: disable=import-outside-toplevel
    ShufersalProvider()
    server.run(transport="streamable-http")