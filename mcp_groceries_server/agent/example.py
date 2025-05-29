import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from mcp_groceries_server.agent.groceries_agent import GroceriesAgent  # noqa: E402


DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)


def main():
    grocery_list = open("./grocery.txt", "r", encoding="utf-8").read()  # pylint: disable=consider-using-with
    if os.path.exists("./preferences.txt"):
        preferences = open("./preferences.txt", "r", encoding="utf-8").read()  # pylint: disable=consider-using-with
    else:
        preferences = ""
    coroutine = GroceriesAgent().invoke(
        shopping_list=grocery_list, preferences=preferences, debug=DEBUG
    )
    result = asyncio.run(coroutine)
    logging.info("Results:\n%s", result["messages"][-1].content)


if __name__ == "__main__":
    main()
