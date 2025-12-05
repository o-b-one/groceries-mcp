# Groceries Agent Documentation

This directory contains the core logic for the Groceries Agent, which orchestrates the grocery shopping process using a Large Language Model (LLM) and various Model Context Protocol (MCP) tools.

## `groceries_agent.py`

This module defines the `GroceriesAgent` class, responsible for the end-to-end grocery shopping automation.

### `create_llm_client(model_id: str)`

A helper function to initialize the appropriate LLM client based on the `model_id` provided.

*   **Parameters:**
    *   `model_id` (str): Identifier for the LLM model (e.g., "gemini-2.0-flash-001", "llama3").
*   **Returns:**
    *   An instance of `ChatGoogleGenerativeAI` for Gemini models or `ChatOllama` for open-source models (llama, qwq, deepseek, mistral).
*   **Raises:**
    *   `ValueError`: If an invalid `model_id` is provided.

### `class GroceriesAgent`

The main class that orchestrates the grocery shopping process.

#### `__init__(self)`

Initializes the `GroceriesAgent` instance.

*   Loads the LLM client using `create_llm_client` with `variables.MODEL_ID`.
*   Initializes a `rich.console.Console` object for status updates.

#### `async invoke(self, shopping_list: str, *, preferences: str = "", debug: bool = False) -> dict`

Executes the grocery shopping process.

*   **Parameters:**
    *   `shopping_list` (str): A string representing the list of items to buy.
    *   `preferences` (str, optional): User-defined preferences for shopping (e.g., "organic only"). Defaults to "".
    *   `debug` (bool, optional): If `True`, enables debug mode for the agent. Defaults to `False`.
*   **Process Flow:**
    1.  Determines the `vendor` from the `MCP_VENDOR` environment variable.
    2.  Configures the path for the `shufersal-mcp` server if the vendor is Shufersal (currently commented out, indicating a single MCP connection).
    3.  Establishes an asynchronous connection to the MCP server, expected to be running at `http://localhost:8000/mcp`.
    4.  Initializes the MCP `ClientSession`.
    5.  Loads available tools from the connected MCP server using `load_mcp_tools`.
    6.  Retrieves the `start_shopping` prompt from the MCP server, injecting the `shopping_list` and `preferences`.
    7.  Creates a ReAct agent using the initialized LLM and loaded tools.
    8.  Invokes the agent with the prepared prompts, including retry logic for `ResourceExhausted` exceptions.
    9.  Provides status updates to the console throughout the process.
*   **Returns:**
    *   `dict`: The result from the agent's invocation, containing the shopping outcome.

## `variables.py`

This module defines configuration variables used by the Groceries Agent.

### `MODEL_ID`

*   **Type:** `str`
*   **Description:** Specifies the ID of the LLM model to be used by the agent.
*   **Source:** Retrieved from the `MODEL_ID` environment variable.
*   **Default Value:** `"gemini-2.0-flash-001"` if the environment variable is not set.