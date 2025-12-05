import os
import typing
import sys
from typing import Optional, Any

from playwright.async_api import async_playwright, Browser, Page
from httpx import AsyncClient
from mcp_groceries_server.server import types

BASE_URL = "https://www.shufersal.co.il/online/he"
CATALOG_ENDPOINT = f"{BASE_URL}/search/results?limit=10"
CART_ENDPOINT = f"{BASE_URL}/cart"

_browser: Optional[Browser] = None
_page: Optional[Page] = None
_playwright_instance: Optional[Any] = None # Added for global playwright instance management

# Default headers for Playwright requests to mimic a real browser
PLAYWRIGHT_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cache-Control": "no-cache",
    "Referer": "https://www.shufersal.co.il/online/he/",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": '?0',
    "Sec-Ch-Ua-Platform": "macOS",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    }


class ShufersalError(Exception):
    def __init__(self, message: str, status: typing.Optional[int] = None):
        super().__init__(message)
        self.status = status


# The _request function will now only be used for the search method as per the plan.
# Other methods will use Playwright.
async def _request(
    url: str, method: str, headers: typing.Dict[str, str] = PLAYWRIGHT_HEADERS, body: typing.Optional[typing.Dict[str, typing.Any]] = None
) -> typing.Any:
    """
    Generate request to Shufersal
    """
    response = None
    async with AsyncClient() as client:
        try:
            response = await client.request(
                method,
                url,
                headers=headers, # Use the passed headers
                json=body if body else None, # Use json parameter for dict body
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
                print("ERR RESP+++ >>>", response.text,file=sys.stderr)
            raise


async def launch_browser(headless: bool = True) -> Page:
    global _browser, _page, _playwright_instance
    if not _browser or not _page:
        _playwright_instance = await async_playwright().start() # Start Playwright instance
        _browser = await _playwright_instance.chromium.launch_persistent_context(
            user_data_dir=os.environ.get("USER_DATA_PATH", "~/groceries_mcp_data/"),
            headless=headless
        )
        _page = await _browser.new_page()
        await _page.goto(BASE_URL)
    return _page

async def close_browser() -> None:
    global _browser, _page, _playwright_instance
    if _page:
        # Some pages sync localstorage on reload
        await _page.reload()
    if _browser:
        await _browser.close()
        _browser = None
        _page = None
    if _playwright_instance:
        await _playwright_instance.stop() # Stop Playwright instance
        _playwright_instance = None

async def _execute_browser_script(page: Page, script: str, args: Optional[typing.Dict[str, typing.Any]] = None) -> Any:
    """
    Executes JavaScript in the browser context with console logging.
    """
    if args is None:
        args = {}
    
    # Inject a console logger into the page context
    await page.evaluate('''() => {
        window.mcpHelper = {
            logs: [],
            originalConsole: {
                log: console.log,
                info: console.info,
                warn: console.warn,
                error: console.error,
            },
        };

        (["log", "info", "warn", "error"]).forEach(method => {
            console[method] = (...args) => {
                window.mcpHelper?.logs.push(`[${method}] ${JSON.stringify(args)}`);
                window.mcpHelper?.originalConsole[method](...args);
            };
        });
    }''')

    # Execute the script
    result = await page.evaluate(script, args)

    # Retrieve logs and restore console
    logs = await page.evaluate('''() => {
        Object.assign(console, window.mcpHelper?.originalConsole);
        const logs = window.mcpHelper?.logs || [];
        delete window.mcpHelper;
        return logs;
    }''')
    
    for log in logs:
        print(f"[Browser Console] {log}", file=sys.stderr)

    return result

async def search(item: str) -> typing.Dict[str, typing.Any]:
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


# Removed _get_cart_as_map and _trigger_update as they are not used and the logic will be handled by Playwright.

async def clear_cart() -> typing.Dict[str, typing.Any]:
    page = await launch_browser()
    script = """
        async () => { # No args needed for clear_cart
            const response = await fetch('/cart/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            const result = await response.json();
            console.log('clear_cart response:', result);
            return result;
        }
    """
    result = await _execute_browser_script(page, script)
    return typing.cast(typing.Dict[str, typing.Any], result) # Cast result to dict

async def update_cart(
    items: list[types.CartItemSchema], reset: bool = False
) -> list[typing.Dict[str, typing.Any]]:
    page = await launch_browser(headless=False)
    results = []
    for item in items:
        selling_method = item.selling_method
        if item.selling_method.lower() == "weight":
            selling_method = "BY_WEIGHT"

        script = """
            async (args) => {
                const response = await window.ajaxCall("/cart/add", JSON.stringify({
                    productCodePost: args.product_id,
                    productCode: args.product_id,
                    sellingMethod: args.sellingMethod,
                    qty: args.qty,
                    frontQuantity: args.qty,
                    comment: "",
                    affiliateCode: ""
                }), () => { }, null, {
                    openFrom: "",
                    recommendationType: "REGULAR"
                });
                console.log('update_cart ajaxCall response:', response);
                return response;
            }
        """
        args = {
            "product_id": str(item.id),
            "sellingMethod": selling_method,
            "qty": int(item.quantity),
        }
        result = await _execute_browser_script(page, script, args)
        results.append(typing.cast(typing.Dict[str, typing.Any], result)) # Cast each result to dict
    return results


async def authorize():
    await launch_browser(headless=False)
