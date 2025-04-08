import json

from mcp_groceries_server.server import server

from . import _service as service
from . import _types


@server.tool()
async def add_items_to_cart(items: list[_types.CartItemSchema]):
    """Add groceries to basket. Result is updated cart"""
    result = await service.update_cart(items)
    return {
        "content": [{"type": "text", "text": json.dumps(result)}],
    }


@server.resource("groceries://search/{item}")
# Setting as tool as a workaround as langchain mcp adapter doesn't support resources yet
@server.tool()
async def search(item: str):
    """Lookup for item on rami levy site"""
    result = await service.search(item)
    items = [transform_product(item) for item in result.get("data", [])]

    return {"content": [{"type": "text", "text": items}]}


def transform_product(product: dict):
    quantity_object = product.get("gs", {}) or {}
    quantity_object = quantity_object.get("Product_Dimensions", {}) or {}
    quantity_object = quantity_object.get("Net_Weight")
    return dict(
        id=product.get("id"),
        name=product.get("name"),
        price=product.get("price", {}).get("price"),
        quantity_evaluation=quantity_object,
    )
