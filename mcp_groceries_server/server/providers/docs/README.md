# Groceries Providers Documentation

This directory defines the interface for grocery providers and contains specific implementations for different vendors.

## `interface/provider.py`

This module defines the abstract base class `Provider`, which all grocery vendor-specific providers must implement. It ensures a consistent interface for interacting with various grocery services.

### `class Provider(abc.ABC)`

An abstract base class that outlines the required methods for any grocery provider. It also handles the registration of these methods as MCP tools and resources.

#### `__init__(self)`

Initializes the `Provider` instance and registers the core grocery actions as MCP tools and resources with the `mcp_groceries_server.server.server` instance.

*   **Registered Tools:**
    *   `add_items_to_cart`: Adds groceries to the basket.
    *   `remove_items_from_cart`: Removes groceries from the basket.
    *   `search`: Looks up an item on the provider's site (also registered as a resource).

#### Abstract Methods

These methods must be implemented by any concrete `Provider` subclass.

*   **`async add_items_to_cart(self, items: list[types.CartItemSchema]) -> dict[str, list[dict]]`**
    *   **Description:** Abstract method to add a list of items to the shopping cart.
    *   **Parameters:**
        *   `items` (list[types.CartItemSchema]): A list of `CartItemSchema` objects representing the items to add.
    *   **Returns:**
        *   `dict[str, list[dict]]`: The updated cart information.

*   **`async remove_items_from_cart(self, items: list[types.CartItemSchema]) -> dict[str, list[dict]]`**
    *   **Description:** Abstract method to remove a list of items from the shopping cart.
    *   **Parameters:**
        *   `items` (list[types.CartItemSchema]): A list of `CartItemSchema` objects representing the items to remove.
    *   **Returns:**
        *   `dict[str, list[dict]]`: The updated cart information.

*   **`async search(self, item: str) -> dict[str, list[dict]]`**
    *   **Description:** Abstract method to search for a specific item on the grocery provider's website. The search term should be in Hebrew.
    *   **Parameters:**
        *   `item` (str): The name of the item to search for.
    *   **Returns:**
        *   `dict[str, list[dict]]`: A dictionary containing search results, typically a list of products.

## Keshet Provider Example

The `keshet/` directory provides a concrete implementation of the `Provider` interface for the Keshet grocery store. Other providers like Rami Levy (`rami_levy/`) and Shufersal (partially implemented in Python, but also with a dedicated TypeScript MCP server) follow a similar structure.

### `keshet/_service.py`

This module contains the low-level functions for interacting with the Keshet API.

*   **Constants:** Defines API endpoints, store IDs, and branch IDs.
*   **`KeshetError`:** A custom exception for Keshet API errors.
*   **`async _request(...)`:** A private helper function for making HTTP requests to the Keshet API, handling authentication (using `VENDOR_API_KEY`) and error responses.
*   **`async search(item: str) -> dict`:** Searches the Keshet catalog for a given item.
*   **`async get_cart() -> list[dict]`:** Retrieves the current items in the Keshet shopping cart.
*   **`async _get_cart_as_map() -> dict[str, int]`:** A helper to get the cart items as a dictionary mapping product ID to quantity.
*   **`async _trigger_update(items: dict[str, int]) -> ...`:** Sends updates to the Keshet cart, including adding, updating, or removing items.
*   **`async remove_from_cart(items_to_remove: list[types.CartItemSchema]) -> list[dict]`:** Removes specified items from the cart.
*   **`async update_cart(items: list[types.CartItemSchema]) -> list[dict]`:** Updates quantities or adds new items to the cart.
*   **Environment Variables:** Relies on `VENDOR_ACCOUNT_ID`, `VENDOR_API_KEY`, and `CART_ID` for authentication and cart management.

### `keshet/tools.py`

This module implements the `Provider` interface using the functions from `keshet/_service.py`.

### `class KeshetProvider(Provider)`

Implements the abstract methods of the `Provider` class for Keshet.

*   **`async add_items_to_cart(self, items: list[types.CartItemSchema]) -> dict[str, list[dict]]`:** Calls `service.update_cart` to add/update items.
*   **`async remove_items_from_cart(self, items: list[types.CartItemSchema]) -> dict[str, list[dict]]`:** Calls `service.remove_from_cart` to remove items.
*   **`async search(self, item: str) -> dict[str, list[dict]]`:** Calls `service.search` and then transforms the raw product data using `transform_product`.
*   **`transform_product(product: dict)`:** A helper function that takes a raw product dictionary from the Keshet API and converts it into a standardized `ProductSchema`-like dictionary.