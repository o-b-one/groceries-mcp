# Groceries MCP Server Documentation

This directory contains the core components of the Python-based Groceries Model Context Protocol (MCP) server.

## `mcp_server.py`

This module initializes the FastMCP server instance.

### `server`

*   **Type:** `FastMCP`
*   **Description:** The main MCP server instance named "Groceries". All tools, resources, and prompts are registered with this server.
*   **Initialization:** The server is initialized using `FastMCP("Groceries")`.
*   **Environment Variables:** It loads environment variables using `dotenv.load_dotenv()` at startup.

## `types.py`

This module defines the Pydantic models and TypedDicts used for data validation and structuring across the Groceries MCP server.

### `class CartItemSchema(pydantic.BaseModel)`

A Pydantic model representing an item in a shopping cart.

*   **`id`** (str): The unique identifier of the item.
*   **`quantity`** (str): The quantity of the product.
*   **`selling_method`** (str, optional): The method of selling (e.g., "units", "weight"). Defaults to an empty string.

#### `_fix_values(cls, data: typing.Any) -> typing.Any`

A `model_validator` that ensures `id` and `quantity` are always converted to strings before model validation.

### `class ProductSchema(typing.TypedDict)`

A TypedDict representing a product retrieved from a grocery provider.

*   **`id`** (str): The unique identifier of the product.
*   **`name`** (str): The name of the product.
*   **`price`** (float, optional): The price of the product.
*   **`quantity_evaluation`** (typing.Dict[str, typing.Any], optional): Details about how the quantity of the product is evaluated (e.g., unit of measure).
*   **`selling_method`** (str, optional): The method of selling for the product.

## `prompts/shopping_prompts.py`

This module defines the prompts that guide the Groceries Agent's behavior.

### `start_shopping(shopping_list: str, preferences: str) -> list[UserMessage]`

This prompt is used to instruct the shopping agent on how to initiate and manage the shopping process.

*   **Registered as:** An MCP prompt using `@server.prompt()`.
*   **Purpose:** To provide detailed instructions to the agent for searching, adding items to the basket, handling out-of-stock items, and concluding the shopping trip.
*   **Parameters:**
    *   `shopping_list` (str): The list of grocery items the user wants to purchase.
    *   `preferences` (str): Any specific user preferences (e.g., "organic only", "cheapest option").
*   **Content Breakdown:**
    *   **Objective:** Clearly states the goal: search, add to basket, and select delivery.
    *   **Important Rules:** Emphasizes not overbuying, default quantity, frugality, removing unseen items, evaluating based on similarity and price, translating to Hebrew, and finding alternatives for out-of-stock items.
    *   **Preferences:** Incorporates user preferences into the agent's decision-making.
    *   **Step 1: Search for items and add to basket:** Guides the agent to search for each item, collect IDs, and use tools to manage the basket.
    *   **Step 2: Conclusion:** Instructs the agent on the required output format: items added, alternatives found, and items not found.