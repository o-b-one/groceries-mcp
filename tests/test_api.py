import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from mcp_groceries_server.agent.api import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_invoke_agent():
    with patch("mcp_groceries_server.agent.api.GroceriesAgent", autospec=True) as MockGroceriesAgent:
        # Configure the mock instance returned by GroceriesAgent()
        mock_agent_instance = MockGroceriesAgent.return_value
        mock_agent_instance.invoke = AsyncMock(return_value={
            "messages": ["", "", {"content": "Mocked shopping result"}]
        })

        response = client.post(
            "/invoke_agent",
            json={
                "groceries_list": ["apples", "bananas"],
                "preferences": "organic"
            }
        )
        assert response.status_code == 200
        assert response.json() == {"result": "Mocked shopping result"}
        mock_agent_instance.invoke.assert_called_once_with(
            shopping_list="apples, bananas",
            preferences="organic"
        )
