import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

from mcp_groceries_server.agent import variables


def create_llm_client(model_id: str):
    if "gemini" in model_id:
        return ChatGoogleGenerativeAI(
            model=model_id,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
    elif any([open_source in model_id for open_source in ["llama", "qwq", "deepseek"]]):
        return ChatOllama(model=model_id, temperature=0, top_k=40, top_p=0.95)
    else:
        raise ValueError(f"Invalid llm model {model_id}")


class GroceriesAgent:
    def __init__(self):
        self._model = create_llm_client(variables.MODEL_ID)

    async def invoke(self, shopping_list: str, *, debug: bool = False) -> dict:
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                "mcp-groceries-server",
                "--vendor",
                "keshet"
                # "rami-levy",
            ],
            transport="stdio",
            env=dict(
                VENDOR_API_KEY=os.environ.get("VENDOR_API_KEY"),
                VENDOR_ACCOUNT_ID=os.environ.get("VENDOR_ACCOUNT_ID"),
                CART_ID=os.environ.get("CART_ID"),
            )
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Get tools
                tools = await load_mcp_tools(session)
                prompts_result = await session.get_prompt(
                    "start_shopping",
                    arguments={
                        "shopping_list": shopping_list,
                        "preferences": """
                    - toilet parper search instead for:
                        lily toilet paper
                    - חלב search for חלב נטול לקטוז instead
                    - Dish soap look for Fairy or פיירי לימון
                    - Chicken Snitzel must not have corn
                    """,
                    },
                )
                agent = create_react_agent(self._model, tools, debug=debug)
                prompts = [msg.content.text for msg in prompts_result.messages]
                return await agent.ainvoke({"messages": prompts}, {"recursion_limit": 15})
