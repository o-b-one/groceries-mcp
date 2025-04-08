import asyncio
import os

from dotenv import load_dotenv

from mcp_groceries_server.agent.groceries_agent import GroceriesAgent

load_dotenv()
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

def main():
    grocery_list = open("./grocery.txt", "r").read()
    coroutine = GroceriesAgent().invoke(shopping_list=grocery_list, debug=DEBUG)
    result = asyncio.run(coroutine)
    print("results:\n", result["messages"][-1].content)
