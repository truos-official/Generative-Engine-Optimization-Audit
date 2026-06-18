import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from stages.stage2 import render_with_playwright, run_stage2
from core.context import AuditContext

@pytest.mark.skip(reason="Requires playwright install")
@pytest.mark.asyncio
async def test_render_with_playwright():
    url = "https://example.com/product/test"

    with patch('playwright.async_api.async_playwright') as mock_pw:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>Rendered</body></html>")

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)
        mock_pw.return_value.__aexit__ = AsyncMock()

        html = await render_with_playwright(url)

        assert html == "<html><body>Rendered</body></html>"

@pytest.mark.asyncio
async def test_run_stage2():
    context = AuditContext(url="https://example.com/product/test")
    context.http_responses = {
        "browser": {"html": "<html><body>Initial</body></html>"}
    }

    config = {}

    with patch('stages.stage2.render_with_playwright') as mock_render:
        mock_render.return_value = "<html><body>Lazy loaded content</body></html>"

        result = await run_stage2(context, config)

        assert result.lazy_loaded_content == "<html><body>Lazy loaded content</body></html>"
        assert "initial_length" in result.js_rendered_diff
