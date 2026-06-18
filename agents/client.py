"""AI agent client for dual-mode testing."""

import os
import re
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
import httpx

# Load environment variables
load_dotenv()


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
        self.azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

        # Initialize clients (disable SSL verify for corporate proxies)
        import httpx
        http_client = httpx.AsyncClient(verify=False)

        self.openai_client = AsyncOpenAI(api_key=self.openai_key, http_client=http_client) if self.openai_key else None
        self.anthropic_client = AsyncAnthropic(api_key=self.anthropic_key, http_client=http_client) if self.anthropic_key else None
        if self.google_key:
            genai.configure(api_key=self.google_key)

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
        elif agent == "bing":
            return await self._call_bing(model, prompt, mode)
        else:
            raise ValueError(f"Unknown agent: {agent}")

    async def _call_openai(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call OpenAI API."""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        messages = [{"role": "user", "content": prompt}]

        # Live mode: enable web search via predicted outputs
        if mode == "live":
            try:
                response = await self.openai_client.chat.completions.create(
                    model=model.name,
                    messages=messages,
                    prediction={"type": "content", "content": "Search the web for current information."}
                )
            except:
                # Fallback if prediction not supported
                response = await self.openai_client.chat.completions.create(
                    model=model.name,
                    messages=messages
                )
        else:
            # Training mode: no web access
            response = await self.openai_client.chat.completions.create(
                model=model.name,
                messages=messages
            )

        text = response.choices[0].message.content or ""

        # Extract URLs from response
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)

        # Estimate cost (simplified)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (input_tokens * 0.000005) + (output_tokens * 0.000015)

        return AgentResponse(
            text=text,
            mode=mode,
            tool_calls=[],
            retrieved_urls=list(set(urls)),
            cost_usd=cost
        )

    async def _call_anthropic(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Anthropic API."""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        # Live mode: enable extended thinking for web search
        if mode == "live":
            try:
                response = await self.anthropic_client.messages.create(
                    model=model.name,
                    max_tokens=4096,
                    thinking={"type": "enabled", "budget_tokens": 2000},
                    messages=[{"role": "user", "content": prompt}]
                )
            except:
                # Fallback without thinking
                response = await self.anthropic_client.messages.create(
                    model=model.name,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
        else:
            # Training mode
            response = await self.anthropic_client.messages.create(
                model=model.name,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

        # Extract text from content blocks
        text = ""
        for block in response.content:
            if block.type == "text":
                text += block.text

        # Extract URLs
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)

        # Estimate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)

        return AgentResponse(
            text=text,
            mode=mode,
            tool_calls=[],
            retrieved_urls=list(set(urls)),
            cost_usd=cost
        )

    async def _call_google(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Google Gemini API."""
        if not self.google_key:
            raise ValueError("Google API key not configured")

        # Configure search grounding for live mode
        if mode == "live":
            try:
                model_obj = genai.GenerativeModel(
                    model_name=model.name,
                    tools="google_search_retrieval"
                )
            except:
                # Fallback without search
                model_obj = genai.GenerativeModel(model_name=model.name)
        else:
            # Training mode: no search
            model_obj = genai.GenerativeModel(model_name=model.name)

        response = await model_obj.generate_content_async(prompt)

        text = response.text if hasattr(response, 'text') else ""

        # Extract URLs
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)

        # Extract grounding metadata if available
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                for chunk in candidate.grounding_metadata.grounding_chunks:
                    if hasattr(chunk, 'web') and chunk.web.uri:
                        urls.append(chunk.web.uri)

        # Estimate cost (free tier / simplified)
        cost = 0.0

        return AgentResponse(
            text=text,
            mode=mode,
            tool_calls=[],
            retrieved_urls=list(set(urls)),
            cost_usd=cost
        )

    async def _call_perplexity(
        self,
        model: ModelConfig,
        prompt: str
    ) -> AgentResponse:
        """Call Perplexity API (always live with search)."""
        if not self.perplexity_key:
            raise ValueError("Perplexity API key not configured")

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model.name,
                    "messages": [{"role": "user", "content": prompt}],
                    "return_citations": True,
                    "return_related_questions": False
                }
            )
            data = response.json()

        text = data["choices"][0]["message"]["content"]

        # Extract citations
        urls = []
        if "citations" in data:
            urls = data["citations"]

        # Estimate cost
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = (input_tokens * 0.000001) + (output_tokens * 0.000001)

        return AgentResponse(
            text=text,
            mode="live",
            tool_calls=[],
            retrieved_urls=urls,
            cost_usd=cost
        )

    async def _call_bing(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Azure OpenAI with Bing grounding."""
        if not self.azure_key or not self.azure_endpoint:
            raise ValueError("Azure OpenAI not configured")

        headers = {
            "api-key": self.azure_key,
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "data_sources": []
        }

        # Live mode: enable Bing grounding
        if mode == "live":
            payload["data_sources"].append({
                "type": "bing",
                "parameters": {
                    "endpoint": "https://api.bing.microsoft.com/",
                    "key": self.azure_key
                }
            })

        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.post(
                self.azure_endpoint,
                headers=headers,
                json=payload
            )
            data = response.json()

        # Extract text from response
        text = data["choices"][0]["message"]["content"]

        # Extract citations if available
        urls = []
        if "context" in data["choices"][0]["message"]:
            context = data["choices"][0]["message"]["context"]
            if "citations" in context:
                for citation in context["citations"]:
                    if "url" in citation:
                        urls.append(citation["url"])

        # Extract URLs from text as fallback
        urls.extend(re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text))

        # Estimate cost
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = (input_tokens * 0.000005) + (output_tokens * 0.000015)

        return AgentResponse(
            text=text,
            mode=mode,
            tool_calls=[],
            retrieved_urls=list(set(urls)),
            cost_usd=cost
        )
