 
import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from rich.console import Console
from google.api_core.exceptions import ResourceExhausted
from logging import getLogger
from mcp_groceries_server.agent import variables
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish

logger = getLogger()


class AgentDebugCallback(BaseCallbackHandler):
    def __init__(self, console: Console):
        self.console = console
        self.step_count = 0

    def on_llm_start(self, serialized, prompts, run_id=None, parent_run_id=None, tags=None, **kwargs):
        self.step_count += 1
        self.console.log(f"\n[bold magenta]Step {self.step_count}:[/bold magenta] Agent thinking...")

    def on_agent_action(self, action: AgentAction, run_id=None, parent_run_id=None, **kwargs):
        self.console.log(f"[bold yellow]Agent Action:[/bold yellow] {action.tool}")
        self.console.log(f"  [dim]Thought:[/dim] {action.log}")
        self.console.log(f"  [dim]Input:[/dim] {action.tool_input}")

    def on_agent_finish(self, finish: AgentFinish, run_id=None, parent_run_id=None, **kwargs):
        self.console.log(f"[bold green]Agent finished:[/bold green]")
        self.console.log(f"  [dim]Output:[/dim] {finish.return_values}")

    def on_tool_start(self, serialized, input_str, run_id=None, parent_run_id=None, tags=None, metadata=None, **kwargs):
        tool_name = serialized.get("name", "unknown")
        self.console.log(f"[bold cyan]→ Executing tool:[/bold cyan] {tool_name}")
        if isinstance(input_str, dict):
            self.console.log(f"  [dim]Parameters:[/dim] {input_str}")

    def on_tool_end(self, output, run_id=None, parent_run_id=None, **kwargs):
        self.console.log(f"[dim]✓ Tool completed[/dim]")

    def on_tool_error(self, error, run_id=None, parent_run_id=None, **kwargs):
        self.console.log(f"[bold red]✗ Tool error:[/bold red] {error}")


MCP_ENDPOINT = os.environ.get("MCP_ENDPOINT", "http://localhost:8000/mcp")
INFERENCE_ENDPOINT = os.environ.get("INFERENCE_ENDPOINT", "http://localhost:1234/v1")
openai_api_base="https://openrouter.ai/api/v1",
def create_llm_client(model_id: str):
    if OPENROUTER_API_KEY := os.environ.get("OPENROUTER_API_KEY"):
        return ChatOpenAI(
            model=model_id,
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
    if GROQ_API_KEY := os.environ.get("GROQ_API_KEY"):
        return ChatOpenAI(
            model=model_id,
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
    if "gemini" in model_id or "gemma" in model_id:
        return ChatGoogleGenerativeAI(
            model=model_id,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
    if any(open_source in model_id for open_source in ["llama","qwen", "qwq", "deepseek", "mistral", "gpt-oss"]):
        return ChatOpenAI(
            model=model_id, 
            base_url=INFERENCE_ENDPOINT,
            api_key="noop",
            temperature=0, 
            top_p=0.95,
            # streaming=True
        )

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
            async with streamablehttp_client(MCP_ENDPOINT, timeout=60 * 60) as (read, write, _):
                async with ClientSession(read, write) as session:
                    # sessions = [session, shufersal_session]
                    # await asyncio.gather(*[session.initialize() for session in sessions])
                    await session.initialize()

                    # Get tools
                    # tools_session = shufersal_session if vendor == "shufersal" else session
                    tools_session = session
                    tools = await load_mcp_tools(tools_session)
                    
                    if debug:
                        self.console.log(f"[bold yellow]Available tools:[/bold yellow] {len(tools)} tools loaded")
                        for tool in tools:
                            self.console.log(f"  - [dim]{tool.name}[/dim]: {tool.description[:80]}...")
                    
                    try:
                        async with asyncio.timeout(60):
                            logger.info("going to try to login")
                            await session.call_tool("user_authorization")
                    except Exception as e:
                        logger.warning(f"Authorization failed with an error: {e}")

                    prompts_result = await session.get_prompt(
                        "start_shopping",
                        arguments={
                            "shopping_list": shopping_list,
                            "preferences": preferences,
                        },
                    )
                    prompts = [msg.content.text for msg in prompts_result.messages]
                    agent = create_react_agent(self._model, tools) 
                    
                    config = {"recursion_limit": 100}
                    
                    status.update(status="[bold green] Shopping for groceries...")
                    if debug:
                        result = await agent.with_retry(
                            retry_if_exception_type=(ResourceExhausted,)
                        ).ainvoke(
                            {"messages": prompts}, config, callbacks=[AgentDebugCallback(self.console)]
                        )
                    else:
                        result = await agent.with_retry(
                            retry_if_exception_type=(ResourceExhausted,)
                        ).ainvoke(
                            {"messages": prompts}, config
                        )
                    status.update(status="[bold green] Shopping completed!")
                    return result
