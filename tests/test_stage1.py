import pytest
from unittest.mock import AsyncMock, patch
from stages.stage1 import fetch_with_user_agent, run_stage1
from core.context import AuditContext

@pytest.mark.asyncio
async def test_fetch_with_user_agent():
    url = "https://example.com/product/test"
    user_agent = "TestBot/1.0"

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.headers = {"content-type": "text/html"}

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await fetch_with_user_agent(url, user_agent)

        assert result["status_code"] == 200
        assert result["html"] == "<html><body>Test</body></html>"
        assert "content-type" in result["headers"]

@pytest.mark.asyncio
async def test_fetch_with_user_agent_timeout():
    url = "https://example.com/product/test"
    user_agent = "TestBot/1.0"

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Timeout"))

        result = await fetch_with_user_agent(url, user_agent)

        assert result["status_code"] == 0
        assert result["error"] is not None

@pytest.mark.asyncio
async def test_run_stage1():
    context = AuditContext(url="https://example.com/product/test")

    config = {
        "crawlers": {
            "user_agents": {
                "browser": "Mozilla/5.0",
                "googlebot": "Googlebot/2.1"
            },
            "timeout": 30
        }
    }

    with patch('stages.stage1.fetch_with_user_agent') as mock_fetch:
        mock_fetch.return_value = {
            "status_code": 200,
            "html": "<html></html>",
            "headers": {},
            "error": None
        }

        result = await run_stage1(context, config)

        assert "browser" in result.http_responses
        assert "googlebot" in result.http_responses
        assert result.locale_valid is False  # No PowerShell cache

@pytest.mark.asyncio
async def test_run_stage1_validates_locale():
    context = AuditContext(url="https://www.example.com/US/en/product/test")

    config = {
        "crawlers": {
            "user_agents": {"browser": "Mozilla/5.0"},
            "timeout": 30
        }
    }

    with patch('stages.stage1.fetch_with_user_agent') as mock_fetch:
        mock_fetch.return_value = {
            "status_code": 200,
            "html": "<html></html>",
            "headers": {},
            "error": None
        }

        result = await run_stage1(context, config)

        assert result.locale_valid is True  # Has US/en pattern
