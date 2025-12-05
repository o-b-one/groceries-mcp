import json

from mcp_groceries_server.server import types
from mcp_groceries_server.server.providers.interface.provider import Provider

from . import _service as service


class ShufersalProvider(Provider):
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
        if not items:
            result = await service.clear_cart()
        else:
            # Set quantity to "0" for each item to be removed via update_cart
            for item in items:
                item.quantity = "0"
            result = await service.update_cart(items)
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
        }


    async def search(self, item: str) -> dict[str, list[dict]]:
        result = await service.search(item)
        items = map(transform_product, result.get("results", []))
        return {"content": [{"type": "text", "text": list(items)}]}
    
    async def authorize(self) -> None:
        await service.authorize()


def transform_product(product: dict):
    return dict(
        id=product.get("baseProduct"),
        name=product.get("baseProductDescription"),
        price=product.get("price", {}).get("value"),
        quantity_evaluation=product.get("pricePerUnit", {}),
        selling_method=product.get("sellingMethod")
    )
