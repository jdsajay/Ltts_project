"""
Ollama Provider (Free, Local)
================================
Uses Ollama for local LLM inference. No API key required.
Install Ollama: https://ollama.ai
Then: ollama pull llama3.2
"""

from __future__ import annotations

from label_compliance.ai.base import AIProvider
from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


class OllamaProvider(AIProvider):
    """Local AI provider using Ollama."""

    def __init__(self) -> None:
        settings = get_settings()
        self._model = settings.ai.local_model
        self._temperature = settings.ai.temperature
        self._max_tokens = settings.ai.max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client()
                logger.info("Ollama connected, model=%s", self._model)
            except ImportError:
                logger.error("ollama package not installed: pip install ollama")
                raise
            except Exception as e:
                logger.error("Cannot connect to Ollama: %s", e)
                raise
        return self._client

    def analyze(self, prompt: str) -> str:
        """Send a text prompt to the local Ollama model."""
        try:
            client = self._get_client()
            response = client.chat(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert in medical device regulatory compliance, "
                            "specifically ISO 14607 (breast implants), ISO 15223-1 (symbols), "
                            "and EU MDR labeling requirements. Analyze the provided information "
                            "and give clear, specific compliance assessments."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": self._temperature, "num_predict": self._max_tokens},
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error("Ollama inference failed: %s", e)
            return f"[Ollama error: {e}]"

    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """Ollama supports multimodal with llava/llama3.2-vision."""
        try:
            client = self._get_client()
            response = client.chat(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_path],
                    },
                ],
                options={"temperature": self._temperature, "num_predict": self._max_tokens},
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error("Ollama multimodal failed: %s", e)
            return f"[Ollama multimodal error: {e}]"

    @property
    def name(self) -> str:
        return f"ollama/{self._model}"
