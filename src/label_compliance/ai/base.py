"""
AI Provider — Abstract Base
==============================
Defines the interface for AI reasoning providers.
Implementations: local (Ollama), API (OpenAI/Anthropic).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


class AIProvider(ABC):
    """Abstract AI provider for compliance reasoning."""

    @abstractmethod
    def analyze(self, prompt: str) -> str:
        """Send a prompt and get a text response."""
        ...

    @abstractmethod
    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """Send a prompt with an image for multimodal analysis."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging."""
        ...


class NoOpProvider(AIProvider):
    """Dummy provider when AI is disabled."""

    def analyze(self, prompt: str) -> str:
        return "[AI disabled — enable via config or .env]"

    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        return "[AI disabled — enable via config or .env]"

    @property
    def name(self) -> str:
        return "none"


def get_ai_provider() -> AIProvider:
    """
    Factory: return the configured AI provider.

    Reads from config/settings.yaml or .env:
      AI_PROVIDER=local    → Ollama (free)
      AI_PROVIDER=openai   → OpenAI API
      AI_PROVIDER=none     → disabled
    """
    settings = get_settings()
    provider_name = settings.ai.provider.lower()

    if provider_name == "local":
        from label_compliance.ai.local import OllamaProvider
        return OllamaProvider()
    elif provider_name == "openai":
        from label_compliance.ai.api import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "none":
        return NoOpProvider()
    else:
        logger.warning("Unknown AI provider '%s', using NoOp", provider_name)
        return NoOpProvider()
