import asyncio
import os
import typing
import sys
from typing import Optional, Any

from playwright.async_api import Playwright, Browser, async_playwright, Page
from httpx import AsyncClient
from mcp_groceries_server.server import types
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.shufersal.co.il/online/he"
AUTH_URL = "https://www.shufersal.co.il/online/he/login"
CATALOG_ENDPOINT = f"{BASE_URL}/search/results?limit=10"
CART_ENDPOINT = f"{BASE_URL}/cart"
STORAGE_STATE = "auth_state.json"

_browser: Optional[Browser] = None
_page: Optional[Page] = None
_context: Optional[Any] = None
_playwright_instance: Optional[Playwright] = None # Added for global playwright instance management

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

STEALTH_JS = """
(() => {
    // Overwrite the `navigator.webdriver` property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });

    // Mock languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['he-IL', 'he', 'en-US', 'en'],
    });

    // Mock plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });

    // Mock chrome property
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };

    // Mock permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
})();
"""


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


async def take_screenshot(page: Page, name: str):
    """Takes a screenshot for debugging purposes."""
    screenshot_dir = "/var/lib/groceries_mcp_data/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    path = os.path.join(screenshot_dir, f"{name}.png")
    await page.screenshot(path=path)
    print(f"Screenshot saved to: {path}", file=sys.stderr)

async def launch_browser() -> Page:
    global _browser, _page, _context, _playwright_instance
    if not _browser or not _page:
        _playwright_instance = await async_playwright().start()
        _browser = await _playwright_instance.chromium.connect(
            os.environ.get("PLAYWRIGHT_WS_URL", "ws://127.0.0.1:3031/"),
            slow_mo=500,
        )
        _context = await _browser.new_context(
            user_agent=PLAYWRIGHT_HEADERS["User-Agent"],
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={"Accept-Language": PLAYWRIGHT_HEADERS["accept-language"]}
        )
        # Apply stealth script to all pages in this context
        await _context.add_init_script(STEALTH_JS)
        _page = await _context.new_page()
        await _page.goto(BASE_URL)
    return _page

async def close_browser() -> None:
    global _browser, _page, _context, _playwright_instance
    if _page:
        await _page.reload()
    if _context:
        await _context.close()
        _context = None
    if _browser:
        await _browser.close()
        _browser = None
        _page = None
    if _playwright_instance:
        await _playwright_instance.stop()
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
    page = await launch_browser()
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
                }), (rsltScript) => {   
                    miglog.cart.cartRefresh(rsltScript);
                    miglog.eventEmitter.emit("cart:addtocartcallback");
                }, null, {
                    openFrom: "SEARCH",
                    recommendationType: "AUTOCOMPLETE_LIST"
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
        try:
            await _execute_browser_script(page, script, args)
            await _page.reload()
            results.append(f"{item.quantity} of {item.id} added")
        except Exception as e:
            print(e)
            results.append(f"{item.quantity} of {item.id} failed to add")
    return results


async def authorize():
    page = await launch_browser()
    try:
        print(f"Navigating to {AUTH_URL}", file=sys.stderr)
        await page.goto(AUTH_URL, wait_until="load")
        
        # Wait for login form to be visible instead of fixed sleep
        try:
            await page.wait_for_selector("#j_username", timeout=10000)
        except Exception:
            print(f"Login form not found, might already be logged in or blocked. {page.url}", file=sys.stderr)
            # await take_screenshot(page, "login_form_not_found")
            if page.url == AUTH_URL:
                raise
            else:
                # If we are not on AUTH_URL, we might be logged in
                return

        if (password := os.environ.get("PASSWORD")) and (username := os.environ.get("USERNAME")):
            print("Filling login credentials", file=sys.stderr)
            await page.fill("#j_username", username)
            await page.fill("#j_password", password)
            
            login_btn = await page.query_selector(".btn-login")
            if login_btn:
                await login_btn.click()
                print("Login button clicked", file=sys.stderr)
            else:
                print("Login button not found", file=sys.stderr)
                # await take_screenshot(page, "login_button_missing")

        urls = [
            # "https://www.shufersal.co.il/online/he/my-account/personal-area/club",
            # BASE_URL,
            BASE_URL + "/A"
        ]

        print("Waiting for redirection after login...", file=sys.stderr)
        tasks = [
            asyncio.create_task(page.wait_for_url(url, timeout=30000))
            for url in urls
        ]
        
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            
            if not done:
                print("Timed out waiting for login redirection", file=sys.stderr)
                # await take_screenshot(page, "login_timeout")
            else:
                print(f"Logged in successfully, current URL: {page.url}", file=sys.stderr)
        except Exception as e:
            print(f"Error during login redirection: {e}", file=sys.stderr)
            # await take_screenshot(page, "login_error")

    except Exception as e:
        print(f"Authorization failed: {e}", file=sys.stderr)
        # await take_screenshot(page, "auth_failed_exception")
    #     await page.context.storage_state(path=STORAGE_STATE)
    # finally:
    #     await close_browser()
