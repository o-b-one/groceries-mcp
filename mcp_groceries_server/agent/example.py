import asyncio
import logging
import os

from dotenv import load_dotenv

from mcp_groceries_server.agent.groceries_agent import GroceriesAgent

load_dotenv()
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)


def main():
    grocery_list = open("./grocery.txt", "r").read()
    coroutine = GroceriesAgent().invoke(shopping_list=grocery_list, debug=DEBUG)
    result = asyncio.run(coroutine)
    logging.info("Results:\n%s", result["messages"][-1].content)


if __name__ == "__main__":
    main()
