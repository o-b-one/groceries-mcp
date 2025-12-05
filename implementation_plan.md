# Implementation Plan

[Overview]
This plan outlines the process to refactor the Shufersal grocery provider's cart management logic in `mcp_groceries_server/server/providers/shufersal/_service.py` to leverage Playwright for `update_cart` and `clear_cart` operations, triggering AJAX calls on shufersal.co.il. This approach involves directly integrating Playwright into the Python codebase, managing browser instances within Python, and executing JavaScript code in the browser context to interact with the Shufersal website's AJAX functionalities. This is a revised plan based on the constraint that the `shufersal-mcp` TypeScript project cannot be modified.

[Types]
No new complex types are introduced. Existing `CartItemSchema` will continue to be used as input for `update_cart`.

[Files]
This plan involves modifications to Python files:
- Modified file: `pyproject.toml` - Add `playwright` as a dependency.
- Modified file: `mcp_groceries_server/server/providers/shufersal/_service.py` - This file will be significantly refactored to:
    - Import `playwright` modules.
    - Implement a mechanism to launch, manage, and close a Playwright browser instance.
    - Update `clear_cart` to use Playwright's `page.evaluate` to execute a `fetch` POST request to `/cart/remove`.
    - Update `update_cart` to use Playwright's `page.evaluate` to execute the `window.ajaxCall` for adding/updating items.
    - The existing `_request` function will be kept for `search` and `get_cart` (if uncommented), as those do not require browser interaction.
- Modified file: `mcp_groceries_server/server/providers/shufersal/tools.py` - Will be updated to call the modified `_service.py` functions, ensuring `remove_items_from_cart` uses `clear_cart` or `update_cart` with `qty: 0` as appropriate.

[Functions]
- New functions (Python):
    - `launch_browser()`: An asynchronous function to launch a Playwright browser instance and return a `Page` object. This will handle browser setup and potentially reuse an existing browser instance.
    - `close_browser()`: An asynchronous function to close the Playwright browser instance.
    - `_execute_browser_script(page: Page, script: str, args: Any)`: A utility function to execute JavaScript within the browser page and return the result.
- Modified function (Python): `clear_cart` in `mcp_groceries_server/server/providers/shufersal/_service.py`. This function will be updated to:
    - Get a Playwright `Page` instance.
    - Call `page.evaluate` to perform a `fetch` POST request to `/cart/remove` with appropriate headers (e.g., `Content-Type`).
- Modified function (Python): `update_cart` in `mcp_groceries_server/server/providers/shufersal/_service.py`. This function will be updated to:
    - Get a Playwright `Page` instance.
    - For each item in the `items` list, call `page.evaluate` to execute the `window.ajaxCall` with the product details.
- Modified function (Python): `remove_items_from_cart` in `mcp_groceries_server/server/providers/shufersal/tools.py`. This function will be updated to utilize the modified `clear_cart` or `<write_to_file>
<path>implementation_plan.md</path>
<content>
# Implementation Plan

[Overview]
This plan outlines the process to refactor the Shufersal grocery provider's cart management logic in `mcp_groceries_server/server/providers/shufersal/_service.py` to leverage Playwright for `update_cart` and `clear_cart` operations, triggering AJAX calls on shufersal.co.il. This approach involves directly integrating Playwright into the Python codebase, managing browser instances within Python, and executing JavaScript code in the browser context to interact with the Shufersal website's AJAX functionalities. This is a revised plan based on the constraint that the `shufersal-mcp` TypeScript project cannot be modified.

[Types]
No new complex types are introduced. Existing `CartItemSchema` will continue to be used as input for `update_cart`.

[Files]
This plan involves modifications to Python files:
- Modified file: `pyproject.toml` - Add `playwright` as a dependency.
- Modified file: `mcp_groceries_server/server/providers/shufersal/_service.py` - This file will be significantly refactored to:
    - Import `playwright` modules.
    - Implement a mechanism to launch, manage, and close a Playwright browser instance.
    - Update `clear_cart` to use Playwright's `page.evaluate` to execute a `fetch` POST request to `/cart/remove`.
    - Update `update_cart` to use Playwright's `page.evaluate` to execute the `window.ajaxCall` for adding/updating items.
    - The existing `_request` function will be kept for `search` and `get_cart` (if uncommented), as those do not require browser interaction.
- Modified file: `mcp_groceries_server/server/providers/shufersal/tools.py` - Will be updated to call the modified `_service.py` functions, ensuring `remove_items_from_cart` uses `clear_cart` or `update_cart` with `qty: 0` as appropriate.

[Functions]
- New functions (Python):
    - `launch_browser()`: An asynchronous function to launch a Playwright browser instance and return a `Page` object. This will handle browser setup and potentially reuse an existing browser instance.
    - `close_browser()`: An asynchronous function to close the Playwright browser instance.
    - `_execute_browser_script(page: Page, script: str, args: Any)`: A utility function to execute JavaScript within the browser page and return the result.
- Modified function (Python): `clear_cart` in `mcp_groceries_server/server/providers/shufersal/_service.py`. This function will be updated to:
    - Get a Playwright `Page` instance.
    - Call `page.evaluate` to perform a `fetch` POST request to `/cart/remove` with appropriate headers (e.g., `Content-Type`).
- Modified function (Python): `update_cart` in `mcp_groceries_server/server/providers/shufersal/_service.py`. This function will be updated to:
    - Get a Playwright `Page` instance.
    - For each item in the `items` list, call `page.evaluate` to execute the `window.ajaxCall` with the product details.
- Modified function (Python): `remove_items_from_cart` in `mcp_groceries_server/server/providers/shufersal/tools.py`. This function will be updated to utilize the modified `clear_cart` or `update_cart` methods from `_service.py`. If `items` is empty, it should call `clear_cart`. Otherwise, it should call `update_cart` with `qty: 0` for each item.

[Classes]
No new classes are introduced. The `ShufersalProvider` class methods will call the modified service functions.

[Dependencies]
- **New Python Dependency:** `playwright`. This will be added to `pyproject.toml`.
- After adding `playwright`, `uv.lock` will need to be updated by running `uv lock`.
- Browser binaries for Playwright will need to be installed by running `playwright install`.

[Testing]
- New unit tests will be required for `clear_cart` and `update_cart` in `mcp_groceries_server/server/providers/shufersal/_service.py` to verify their Playwright-based implementation. These tests will need to mock Playwright browser and page interactions.
- Existing tests for `ShufersalProvider` in `mcp_groceries_server/server/providers/shufersal/tools.py` will be updated to reflect the new underlying implementation, potentially mocking the `_service.py` calls.

[Implementation Order]
1. Add `playwright` to `pyproject.toml` and run `uv lock` and `playwright install`.
2. Refactor `mcp_groceries_server/server/providers/shufersal/_service.py`:
    a. Import `playwright` modules.
    b. Implement `launch_browser()` and `close_browser()` for browser management.
    c. Implement `_execute_browser_script()`.
    d. Update `clear_cart` to use Playwright with a `fetch` call.
    e. Update `update_cart` to use Playwright with `window.ajaxCall`.
    f. Update the existing `_request` function to only be used for `search` method.
3. Update `mcp_groceries_server/server/providers/shufersal/tools.py` to use the refactored `_service.py` methods correctly, especially for `remove_items_from_cart`.
4. Add new unit tests and update existing ones for the Playwright integration.
