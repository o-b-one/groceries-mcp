import json
import logging

from mcp_groceries_server.server import types
from mcp_groceries_server.server.providers.interface.provider import Provider

from . import _service as service

logger = logging.getLogger(__name__)


class KeshetProvider(Provider):
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
        products = (
            result.get("suggestions", {}).get("suggestProducts", {}).get("products", [])
        )
        items = [transform_product(item) for item in products]
        logger.info(f"Found {len(items)} items for {item}: {items}")
        return {"content": [{"type": "text", "text": items}]}


def transform_product(product: dict):
    quantity_object = product.get("original", {}).get("unitOfMeasure", {}) or {}
    return dict(
        id=product.get("id"),
        name=product.get("localName"),
        price=product.get("branch", {}).get("regularPrice"),
        quantity_evaluation=quantity_object,
    )
