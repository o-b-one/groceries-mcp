import datetime
import os
import sys
import typing

from httpx import AsyncClient

from mcp_groceries_server.server import types

CART_QUERY_ENDPOINT = f"https://www-api.rami-levy.co.il/api/v2/site/clubs/customer/{os.environ['VENDOR_ACCOUNT_ID']}"
STORE_ID = "1219"  # ONLINE STORE ID
BRANCH_ID = "2725"
BASE_URL = (
    f"https://www.keshet-teamim.co.il/v2/retailers/{STORE_ID}/branches/{BRANCH_ID}"
)
CART_UPDATE_ENDPOINT = f"{BASE_URL}/carts/{os.environ['CART_ID']}?appId=4"
CATALOG_ENDPOINT = f"{BASE_URL}/products/autocomplete?appId=4&filters=%7B%22must%22:%7B%22exists%22:%5B%22family.id%22,%22family.categoriesPaths.id%22,%22branch.regularPrice%22%5D,%22term%22:%7B%22branch.isActive%22:true,%22branch.isVisible%22:true%7D%7D,%22mustNot%22:%7B%22term%22:%7B%22branch.regularPrice%22:0%7D%7D,%22bool%22:%7B%22should%22:%5B%7B%22bool%22:%7B%22must_not%22:%7B%22exists%22:%7B%22field%22:%22branch.outOfStockShowUntilDate%22%7D%7D%7D%7D,%7B%22bool%22:%7B%22must%22:%5B%7B%22range%22:%7B%22branch.outOfStockShowUntilDate%22:%7B%22gt%22:%22now%22%7D%7D%7D,%7B%22term%22:%7B%22branch.isOutOfStock%22:true%7D%7D%5D%7D%7D,%7B%22bool%22:%7B%22must%22:%5B%7B%22term%22:%7B%22branch.isOutOfStock%22:false%7D%7D%5D%7D%7D%5D%7D%7D&from=0&isSearch=true&languageId=1&size=10"


class KeshetError(Exception):
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
        "accept": "*/*",
        "content-type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {os.environ['VENDOR_API_KEY']}",
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
            timeout=30.0,
        )

        if (response.status_code // 100) != 2:
            raise KeshetError(
                f"Request failed with message {response}, {response.status_code}",
                response.status_code,
            )
        return response.json()


async def search(item: str) -> dict:
    return await _request(url=f"{CATALOG_ENDPOINT}&query={item}", method="GET")


async def get_cart() -> list[dict]:
    response = await _trigger_update({})
    cart = response.get("cart", {}) or {}
    cart_items = cart.get("lines", []) or {}
    return [
        types.CartItemSchema(
            id=str(item["id"]), quantity=str(item["quantity"])
        ).model_dump()
        for item in cart_items
    ]


async def _get_cart_as_map() -> dict[str, int]:
    cart = await get_cart()
    return {item["id"]: item["quantity"] for item in cart}


async def _trigger_update(items: dict[str, int]) -> typing.Coroutine[None, None, None]:
    formatted_items = [
        {
            "quantity": int(quantity),
            "soldBy": None,
            "retailerProductId": int(_id),
            "type": 1,
            **(dict(delete=True, isCase=False) if not quantity else {}),
        }
        for _id, quantity in items.items()
    ]
    result = await _request(
        url=CART_UPDATE_ENDPOINT,
        body={
            "lines": formatted_items,
            "deliveryProduct_Id": 3766099,
            "deliveryType": 1,
            "source": "Autocomplete Results",
        },
        headers={"x-http-method-override": "PATCH"},
    )
    return result


async def remove_from_cart(items_to_remove: list[types.CartItemSchema]) -> list[dict]:
    cart = await get_cart()
    for item in items:
        cart[item["id"]] = 0
    return await _trigger_update(cart)


async def update_cart(items: list[types.CartItemSchema]) -> list[dict]:
    cart = await _get_cart_as_map()
    for item in items:
        cart[item.id] = item.quantity
    return await _trigger_update(cart)
