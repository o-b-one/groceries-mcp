import json
import sys
import traceback
from mcp_groceries_server.server import server

from . import _service as service
from mcp_groceries_server.server import types 


@server.tool()
async def add_items_to_cart(items: list[types.CartItemSchema]):
    """Add groceries to basket. Result is updated cart"""
    result = await service.update_cart(items)
    return {
        "content": [{"type": "text", "text": json.dumps(result)}],
    }


@server.tool()
async def remove_items_from_cart(items: list[types.CartItemSchema]):
    """Remove groceries from basket. Result is updated cart"""
    result = await service.remove_from_cart(items)
    return {
        "content": [{"type": "text", "text": json.dumps(result)}],
    }


@server.resource("groceries://search/{item}")
# Setting as tool as a workaround as langchain mcp adapter doesn't support resources yet
@server.tool()
async def search(item: str):
    """Lookup for item on rami levy site"""
    result = await service.search(item)
    products = result.get("suggestions", {}).get("suggestProducts", {}).get("products", [])
    items = [transform_product(item) for item in products]
    return {"content": [{"type": "text", "text": items}]}


def transform_product(product: dict):
    quantity_object = product.get("original", {}).get("unitOfMeasure", {}) or {}
    return dict(
        id=product.get("id"),
        name=product.get("localName"),
        price=product.get("price", {}).get("price"),
        quantity_evaluation=quantity_object,
    )
