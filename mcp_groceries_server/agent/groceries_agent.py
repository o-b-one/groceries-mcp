
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from rich.console import Console
from google.api_core.exceptions import ResourceExhausted

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
    if any(open_source in model_id for open_source in ["llama", "qwq", "deepseek", "mistral"]):
        return ChatOllama(model=model_id, temperature=0, top_k=40, top_p=0.95, format="json")

    raise ValueError(f"Invalid llm model {model_id}")


class GroceriesAgent:
    def __init__(self):
        self._model = create_llm_client(variables.MODEL_ID)
        self.console = Console()

    async def invoke(
        self, shopping_list: str, *, preferences: str = "", debug: bool = False
    ) -> dict:
        self.console.log("GroceriesAgent: Starting shopping session...")
        with self.console.status("[bold green] Start shopping") as status:
            # async with stdio_client(main_server_params) as (read, write), stdio_client(shufersal_server_params) as (sread, swrite) :
            #     async with ClientSession(read, write) as session, ClientSession(sread, swrite) as shufersal_session:
            async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
                async with ClientSession(read, write) as session:
                    # sessions = [session, shufersal_session]
                    # await asyncio.gather(*[session.initialize() for session in sessions])
                    await session.initialize()

                    # Get tools
                    # tools_session = shufersal_session if vendor == "shufersal" else session
                    tools_session = session
                    tools = await load_mcp_tools(tools_session)

                    prompts_result = await session.get_prompt(
                        "start_shopping",
                        arguments={
                            "shopping_list": shopping_list,
                            "preferences": preferences,
                        },
                    )
                    agent = create_react_agent(self._model, tools, debug=True, version="v2")
                    prompts = [msg.content.text for msg in prompts_result.messages]
                    status.update(status="[bold green] Shopping for groceries...")
                    result = await agent.with_retry(
                        retry_if_exception_type=(ResourceExhausted,)
                    ).ainvoke(
                        {"messages": prompts}, {"recursion_limit": 100}
                    )
                    status.update(status="[bold green] Shopping completed!")
                    return result
