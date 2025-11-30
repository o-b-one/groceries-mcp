import os
import typing
import sys
import json

from httpx import AsyncClient
from mcp_groceries_server.server import types

BASE_URL = "https://www.shufersal.co.il/online/he"
CATALOG_ENDPOINT = f"{BASE_URL}/search/results?limit=10"
CART_ENDPOINT = f"{BASE_URL}/cart"


class ShufersalError(Exception):
    def __init__(self, message: str, status: typing.Optional[int] = None):
        super().__init__(message)
        self.status = status


async def _request(
    url: str, method: str, headers: dict = {}, body: typing.Optional[dict] = None
) -> typing.Coroutine[typing.Any, None, None]:
    """
    Generate request to Shufersal
    """

    DEFAULT_HEADERS = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7",
        "User-Agent": "",
        "Cache-Control": "no-cache",
        "Cookie": "",
        "Referer": "https://www.shufersal.co.il/online/he/%D7%A7%D7%98%D7%92%D7%95%D7%A8%D7%99%D7%95%D7%AA/%D7%A1%D7%95%D7%A4%D7%A8%D7%9E%D7%A8%D7%A7%D7%98/%D7%A9%D7%95%D7%91%D7%A8%D7%99%D7%9D-%D7%A9%D7%99%D7%90%D7%99%D7%9D-%D7%91%D7%9E%D7%91%D7%A6%D7%A2%D7%99%D7%9D/c/A500701/promotion?promo=4161816&shuf_source=shufersal_DY&shuf_medium=Long_Banner_S&shuf_campaign=pasta&shuf_content=shufersal_pasta_030625&shuf_term=DY",
        "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "Sec-Ch-Ua-Mobile": '?0',
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    response = None
    async with AsyncClient() as client:
        try:
            response = await client.request(
                method,
                url,
                headers={
                    **DEFAULT_HEADERS,
                    **headers,
                },
                data=body if body else None,
            )
            if (response.status_code // 100) != 2:
                raise ShufersalError(
                    f"Request failed with message {response}, {response.status_code}",
                    response.status_code,
                )
            return response.json()
        except Exception as e:
            print(f"ERR+++ {str(body)} >>>", method, url, type(e), e, file=sys.stderr)
            if response:
                print(f"ERR RESP+++ >>>", response.text,file=sys.stderr)
            raise


async def search(item: str) -> dict:
    return await _request(
        url=f"{CATALOG_ENDPOINT}&q={item}:relevance",
        method="GET"
    )


# async def get_cart() -> list[dict]:
#     response = await _request(url=CART_QUERY_ENDPOINT, method="GET")
#     cart = response.get("cart", {}) or {}
#     cart_items = cart.get("items", {}) or {}
#     return [
#         types.CartItemSchema(id=str(_id), quantity=str(quantity)).model_dump()
#         for _id, quantity in cart_items.items()
#     ]


async def _get_cart_as_map() -> dict[str, int]:
    cart = await get_cart()
    return {item.get("id"): item.get("quantity") for item in cart}


async def _trigger_update(items: dict[str, int]) -> typing.Coroutine[None, None, None]:
    for product in items.keys():
        await _request(
            url=f"{CART_ENDPOINT}/add?cartContext%5BopenFrom%5D=PROMOTION&cartContext%5BrecommendationType%5D=REGULAR",
            method="POST",
            headers={
                "csrftoken": os.environ['VENDOR_API_KEY'],
            },
            body={
                "productCode":product,
                "productCodePost": product, 
                "sellingMethod":"BY_UNIT",
                "qty": str(items[product]),
                "frontQuantity": str(items[product]),
                "comment":"",
                "affiliateCode":""
            },
        )


async def clear_cart() -> None:
    return _request(
        url=f"{CART_ENDPOINT}/remove",
        method="POST",
        body={}
    )


async def update_cart(
    items: list[types.CartItemSchema], reset: bool = False
) -> list[dict]:
    for item in items:
        match item.selling_method.lower():
            case "weight":
                selling_method = "BY_WEIGHT"
            case _:
                selling_method = item.selling_method

        await _request(
                url=f"{CART_ENDPOINT}/add?cartContext%5BopenFrom%5D=PROMOTION&cartContext%5BrecommendationType%5D=REGULAR",
                method="POST",
                body={
                    "productCode":str(item.id),
                    "productCodePost": str(item.id), 
                    "sellingMethod": selling_method,
                    "qty": str(item.quantity),
                    "frontQuantity": str(item.quantity),
                    "comment":"",
                    "affiliateCode":""
                },
                headers={
                    "csrftoken": os.environ['VENDOR_API_KEY']
                }
            )