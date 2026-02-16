"""AI subpackage — local (Ollama) and API (OpenAI) providers."""

from label_compliance.ai.base import AIProvider, get_ai_provider

__all__ = ["AIProvider", "get_ai_provider"]
