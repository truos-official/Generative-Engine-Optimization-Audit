"""AI agent client for dual-mode testing."""

import os
from dataclasses import dataclass
from typing import Literal


@dataclass
class ModelConfig:
    name: str
    provider: str
    tier: str


@dataclass
class AgentResponse:
    text: str
    mode: Literal["training", "live"]
    tool_calls: list[dict]
    retrieved_urls: list[str]
    cost_usd: float


class AgentClient:
    """Client for calling AI agents in training and live modes."""

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")

    async def call_agent(
        self,
        agent: str,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call agent in specified mode."""
        if agent == "openai":
            return await self._call_openai(model, prompt, mode)
        elif agent == "anthropic":
            return await self._call_anthropic(model, prompt, mode)
        elif agent == "google":
            return await self._call_google(model, prompt, mode)
        elif agent == "perplexity":
            return await self._call_perplexity(model, prompt)
        else:
            raise ValueError(f"Unknown agent: {agent}")

    async def _call_openai(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call OpenAI API (simplified)."""
        # Simplified - would use actual OpenAI SDK
        return AgentResponse(
            text=f"OpenAI {mode} response",
            mode=mode,
            tool_calls=[],
            retrieved_urls=[],
            cost_usd=0.01
        )

    async def _call_anthropic(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Anthropic API (simplified)."""
        return AgentResponse(
            text=f"Anthropic {mode} response",
            mode=mode,
            tool_calls=[],
            retrieved_urls=[],
            cost_usd=0.01
        )

    async def _call_google(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Google API (simplified)."""
        return AgentResponse(
            text=f"Google {mode} response",
            mode=mode,
            tool_calls=[],
            retrieved_urls=[],
            cost_usd=0.01
        )

    async def _call_perplexity(
        self,
        model: ModelConfig,
        prompt: str
    ) -> AgentResponse:
        """Call Perplexity API (always live)."""
        return AgentResponse(
            text="Perplexity response",
            mode="live",
            tool_calls=[],
            retrieved_urls=[],
            cost_usd=0.01
        )
