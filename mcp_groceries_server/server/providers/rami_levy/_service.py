import datetime
import os
import typing

from httpx import AsyncClient

from mcp_groceries_server.server import types 

BASE_URL = "https://www.rami-levy.co.il/api"
CATALOG_ENDPOINT = f"{BASE_URL}/catalog"
CART_UPDATE_ENDPOINT = f"{BASE_URL}/v2/cart"
CART_QUERY_ENDPOINT = f"https://www-api.rami-levy.co.il/api/v2/site/clubs/customer/{os.environ['VENDOR_ACCOUNT_ID']}"
STORE_ID = "331"  # ONLINE STORE ID


class RamiLevyError(Exception):
    def __init__(self, message: str, status: typing.Optional[int] = None):
        super().__init__(message)
        self.status = status


async def _request(
    url: str, method: str = "POST", headers: dict = {}, body: dict = {}
) -> typing.Coroutine[typing.Any, None, None]:
    """
    Generate request to RamiLevy
    """

    DEFAULT_HEADERS = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {os.environ['VENDOR_API_KEY']}",
        "ecomtoken": os.environ["VENDOR_API_KEY"],
        "locale": "he",
    }
    async with AsyncClient() as client:
        response = await client.request(
            method,
            url,
            headers={
                **DEFAULT_HEADERS,
                **headers,
            },
            **(dict(json=body if body else {})),
        )

        if (response.status_code // 100) != 2:
            raise RamiLevyError(
                f"Request failed with message {response}, {response.status_code}",
                response.status_code,
            )

        return response.json()


async def search(item: str) -> dict:
    return await _request(
        url=CATALOG_ENDPOINT,
        body=dict(
            q=item,
            store=STORE_ID,
            aggs=1,
        ),
    )


async def get_cart() -> list[dict]:
    response = await _request(url=CART_QUERY_ENDPOINT, method="GET")
    cart = response.get("cart", {}) or {}
    cart_items = cart.get("items", {}) or {}
    return [
        types.CartItemSchema(id=str(_id), quantity=str(quantity)).model_dump()
        for _id, quantity in cart_items.items()
    ]


async def _get_cart_as_map() -> dict[str, int]:
    cart = await get_cart()
    return {item.get("id"): item.get("quantity") for item in cart}


async def _trigger_update(items: dict[str, int]) -> typing.Coroutine[None, None, None]:
    await _request(
        url=CART_UPDATE_ENDPOINT,
        body=dict(
            store=STORE_ID,
            isClub=0,
            supplyAt=(
                datetime.datetime.utcnow() + datetime.timedelta(days=1)
            ).isoformat(),
            items=items,
            meta=None,
        ),
    )


async def remove_from_cart(items_to_remove: list[types.CartItemSchema]) -> list[dict]:
    cart = await _get_cart_as_map()
    for item in items_to_remove:
        del cart[item.id]

    await update_cart(cart)
    return await get_cart()


async def update_cart(
    items: list[types.CartItemSchema], reset: bool = False
) -> list[dict]:
    new_cart = {}
    if not reset:
        new_cart = await _get_cart_as_map()

    for item in items:
        new_cart[item.id] = item.quantity

    await _trigger_update(new_cart)
    return await get_cart()
