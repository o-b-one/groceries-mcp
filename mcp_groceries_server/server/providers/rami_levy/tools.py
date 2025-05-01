import json

from mcp_groceries_server.server import types
from mcp_groceries_server.server.providers.interface.provider import Provider

from . import _service as service


class RamiLevyProvider(Provider):
    async def add_items_to_cart(
        self, items: list[types.CartItemSchema]
    ) -> dict[str, list[dict]]:
        result = await service.update_cart(items)
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
        }

    async def remove_items_from_cart(
        self, items: list[types.CartItemSchema]
    ) -> dict[str, list[dict]]:
        result = await service.remove_from_cart(items)
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
        }

    async def search(self, item: str) -> dict[str, list[dict]]:
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
