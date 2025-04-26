# Groceries MCP Server
---

MCP Server for different Groceries vendor API, enabling searching groceries and cart update.  

### Features

- **Automatic cart creation**: add items to the cart based on a provided list
- **Groceries lookup**: lookup for groceries using vendor API

## Tools
1. `add_items_to_cart`
  - Add groceries to the basket. 
  - Inputs:
    - `items`(list[CartItemScheam]): items to add to the cart
  - Returns: Updated cart
2. `search`
   - Lookup for item in the vendor
   - Inputs:
     - `item` (string): Items to 
   - Returns: list of items corresponding to search term


## Setup


## Extract Environment Variables

### Rami Levy
1. log in to the Rami Levy site
2. In developer tools (click on F12) and execute:
```js
const state = JSON.parse(localStorage.ramilevy);
console.log({
    "VENDOR_ACCOUNT_ID": state.authuser.user.id,
    "VENDOR_API_KEY": state.authuser.user.token,
});
```
3. Replace environment variables with the printed values


### Local usage 
1. Update the `.env` file using `env.template` (requires Gemini)
2. Update the `grocery.txt`
3. Run `make compile start_agent`

### Usage with Claude Desktop
To use this with Claude Desktop, add the following to your `claude_desktop_config.json`:

#### UV
```json
{
  "mcpServers": {
    "groceries": {
      "command": "uv",
      "args": [
        "run",
        "mcp-groceries-server",
        "--vendor",
        vendorName # rami-levy, keshet e.g
      ],
      "env":{
        "VENDOR_API_KEY": "<YOUR_API_TOKEN>",
        "VENDOR_ACCOUNT_ID": "<VENDOR_ACCOUNT_ID>"
      }
    }
  }
}
```

## Build

Docker build:

```bash
docker build -t mcp-groceries-server .
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
