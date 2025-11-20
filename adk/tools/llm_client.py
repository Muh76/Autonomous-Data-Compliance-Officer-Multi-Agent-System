"""Unified interface for LLM providers."""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from ..config import get_config
from ..core.logger import get_logger

logger = get_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate text stream from a prompt."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI LLM client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
            logger.info("OpenAI client initialized", model=model)
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI."""
        import asyncio
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.client.api_key)
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate streaming text using OpenAI."""
        import asyncio
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.client.api_key)
        
        stream = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicClient(LLMClient):
    """Anthropic Claude LLM client."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
            logger.info("Anthropic client initialized", model=model)
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic."""
        import asyncio
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=self.client.api_key)
        
        response = await client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 2000),
            messages=[{"role": "user", "content": prompt}],
        )
        
        return response.content[0].text
    
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate streaming text using Anthropic."""
        import asyncio
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=self.client.api_key)
        
        async with client.messages.stream(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 2000),
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

class VertexAIClient(LLMClient):
    """Google Vertex AI LLM client."""
    
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1", model: str = "gemini-pro"):
        try:
            from langchain_google_vertexai import VertexAI
            # If project_id is None, it will attempt to infer from environment
            self.client = VertexAI(project=project_id, location=location, model_name=model)
            self.model = model
            logger.info("Vertex AI client initialized", model=model, project=project_id)
        except ImportError:
            raise ImportError("langchain-google-vertexai not installed. Install with: pip install langchain-google-vertexai")
        except Exception as e:
            # Fallback for local development without full GCP credentials
            logger.warning("Failed to initialize Vertex AI, trying Google GenAI (API Key)", error=str(e))
            raise e

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Vertex AI."""
        try:
            return self.client.invoke(prompt)
        except Exception as e:
            logger.error("Vertex AI generation failed", error=str(e))
            raise e

    async def generate_stream(self, prompt: str, **kwargs):
        """Generate streaming text using Vertex AI."""
        for chunk in self.client.stream(prompt):
            yield chunk

def get_llm_client() -> LLMClient:
    """
    Get LLM client based on configuration.
    
    Returns:
        LLM client instance
    """
    config = get_config()
    llm_config = config.get("llm", {})
    
    provider = llm_config.get("provider", "openai")
    model = llm_config.get("model", "gpt-4-turbo-preview")
    
    if provider == "openai":
        api_key = llm_config.get("openai_api_key")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        return OpenAIClient(api_key=api_key, model=model)
    elif provider == "anthropic":
        api_key = llm_config.get("anthropic_api_key")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return AnthropicClient(api_key=api_key, model=model)
    elif provider == "vertex":
        project_id = llm_config.get("google_project_id")
        location = llm_config.get("google_location", "us-central1")
        return VertexAIClient(project_id=project_id, location=location, model=model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")




