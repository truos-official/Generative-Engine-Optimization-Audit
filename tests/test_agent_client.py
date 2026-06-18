import pytest
from agents.client import AgentClient, ModelConfig

@pytest.mark.asyncio
async def test_agent_client_openai_training():
    client = AgentClient()
    model = ModelConfig(name="gpt-4o", provider="openai", tier="flagship")

    response = await client.call_agent("openai", model, "Test prompt", "training")

    assert response.mode == "training"
    assert response.text is not None
    assert isinstance(response.cost_usd, float)

@pytest.mark.asyncio
async def test_agent_client_openai_live():
    client = AgentClient()
    model = ModelConfig(name="gpt-4o", provider="openai", tier="flagship")

    response = await client.call_agent("openai", model, "Test prompt", "live")

    assert response.mode == "live"
    assert isinstance(response.retrieved_urls, list)

@pytest.mark.asyncio
async def test_agent_client_perplexity():
    client = AgentClient()
    model = ModelConfig(name="sonar-pro", provider="perplexity", tier="flagship")

    response = await client.call_agent("perplexity", model, "Test prompt", "live")

    assert response.mode == "live"
