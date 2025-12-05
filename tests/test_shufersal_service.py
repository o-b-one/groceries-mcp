import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from mcp_groceries_server.server.providers.shufersal import _service as service
from mcp_groceries_server.server.types import CartItemSchema

@pytest.fixture
def mock_playwright_page():
    """Mocks a Playwright Page object."""
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value={}) # Default return for evaluate
    return mock_page

@pytest.fixture
def mock_playwright_browser(mock_playwright_page):
    """Mocks a Playwright Browser object."""
    mock_browser = AsyncMock()
    mock_browser.new_page.return_value = mock_playwright_page
    mock_browser.close = AsyncMock()
    return mock_browser

@pytest.fixture
def mock_async_playwright(mock_playwright_browser):
    """Mocks the async_playwright context."""
    mock_pw = AsyncMock()
    mock_pw.chromium.launch.return_value = mock_playwright_browser
    mock_pw.start.return_value = mock_pw # Mock the start() method
    mock_pw.stop.return_value = None # Mock the stop() method
    return mock_pw

@pytest.mark.asyncio
async def test_clear_cart(mock_playwright_page, mock_async_playwright):
    with patch('playwright.async_api.async_playwright', return_value=mock_async_playwright):
        # Reset globals for isolated test
        service._browser = None
        service._page = None
        service._playwright_instance = None

        await service.clear_cart()

        mock_async_playwright.start.assert_awaited_once()
        mock_playwright_page.goto.assert_awaited_with(service.BASE_URL)
        # Check the script executed
        mock_playwright_page.evaluate.assert_any_call(
            """
        async () => { # No args needed for clear_cart
            const response = await fetch('/cart/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            const result = await response.json();
            console.log('clear_cart response:', result);
            return result;
        }
    """, {} # No args passed to clear_cart script
        )
        # Ensure browser is not closed immediately after clear_cart
        mock_playwright_page.close.assert_not_awaited()
        mock_playwright_browser.close.assert_not_awaited()
        mock_async_playwright.stop.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_cart(mock_playwright_page, mock_async_playwright):
    with patch('playwright.async_api.async_playwright', return_value=mock_async_playwright):
        # Reset globals for isolated test
        service._browser = None
        service._page = None
        service._playwright_instance = None
        
        items_to_update = [
            CartItemSchema(id="123", quantity="2", selling_method="unit"),
            CartItemSchema(id="456", quantity="1", selling_method="weight"),
        ]

        await service.update_cart(items_to_update)

        mock_async_playwright.start.assert_awaited_once()
        mock_playwright_page.goto.assert_awaited_with(service.BASE_URL)

        # Check each item's script execution
        expected_script_part = """
            async (args) => {
                const response = await window.ajaxCall("/cart/add", JSON.stringify({
                    productCodePost: args.product_id,
                    productCode: args.product_id,
                    sellingMethod: args.sellingMethod,
                    qty: args.qty,
                    frontQuantity: args.qty,
                    comment: "",
                    affiliateCode: ""
                }), () => { }, null, {
                    openFrom: "BROWSER_AUTOMATION", # Custom context to identify calls
                    recommendationType: "REGULAR"
                });
                console.log('update_cart ajaxCall response:', response);
                return response;
            }
        """

        mock_playwright_page.evaluate.assert_any_call(
            expected_script_part,
            {"product_id": "123", "sellingMethod": "unit", "qty": 2}
        )
        mock_playwright_page.evaluate.assert_any_call(
            expected_script_part,
            {"product_id": "456", "sellingMethod": "BY_WEIGHT", "qty": 1}
        )
        # Ensure browser is not closed immediately after update_cart
        mock_playwright_page.close.assert_not_awaited()
        mock_playwright_browser.close.assert_not_awaited()
        mock_async_playwright.stop.assert_not_awaited()

# Add a test to ensure the browser is closed
@pytest.mark.asyncio
async def test_close_browser():
    # Manually set up a mock browser and page for this specific test
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    mock_browser.new_page.return_value = mock_page
    mock_pw.chromium.launch.return_value = mock_browser
    mock_pw.start.return_value = mock_pw
    mock_pw.stop.return_value = None

    with patch('playwright.async_api.async_playwright', return_value=mock_pw):
        # Ensure browser is launched
        await service.launch_browser()
        try:
            assert service._browser is not None
            assert service._page is not None
            assert service._playwright_instance is not None
        finally:
            await service.close_browser()

        mock_browser.close.assert_awaited_once()
        mock_pw.stop.assert_awaited_once()
        assert service._browser is None
        assert service._page is None
        assert service._playwright_instance is None
