from fastapi import FastAPI
from pydantic import BaseModel
from mcp_groceries_server.agent.groceries_agent import GroceriesAgent

app = FastAPI()
agent = GroceriesAgent()

class GroceriesRequest(BaseModel):
    groceries_list: list[str]
    preferences: str = ""

@app.post("/execute")
async def execute(request: GroceriesRequest):
    shopping_list_str = ", ".join(request.groceries_list)
    result = await agent.invoke(shopping_list=f"<shopping_list>{shopping_list_str}</shopping_list>", preferences=request.preferences)
    return {"result": result["messages"][-1].content}

@app.get("/health")
def healthcheck():
    return "SUCCESS"
