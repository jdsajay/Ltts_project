"""
Ollama Provider (Free, Local)
================================
Uses Ollama for local LLM inference. No API key required.
Install Ollama: https://ollama.ai
Then: ollama pull llama3.2-vision  (for image analysis)
      ollama pull llama3.2          (for fast text analysis)

Two models are supported:
- Vision model (llama3.2-vision): used for image-based analysis
- Text model (llama3.2): used for fast text-only analysis (3B, much faster)
"""

from __future__ import annotations

import time

from label_compliance.ai.base import AIProvider
from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# System prompt kept short — small models do better with concise instructions
_SYSTEM_PROMPT = (
    "You are an ISO compliance auditor for medical device labels. "
    "Always respond with valid JSON only. No markdown, no extra text."
)


class OllamaProvider(AIProvider):
    """Local AI provider using Ollama with dual-model support.

    Uses a fast text model for OCR text analysis and a vision model
    for image-based verification. Both enforce JSON output mode.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._vision_model = settings.ai.local_model  # e.g. llama3.2-vision
        self._text_model = getattr(settings.ai, "text_model", None) or "llama3.2"
        self._temperature = settings.ai.temperature
        self._max_tokens = settings.ai.max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client()
                logger.info(
                    "Ollama connected — vision=%s, text=%s",
                    self._vision_model, self._text_model,
                )
            except ImportError:
                logger.error("ollama package not installed: pip install ollama")
                raise
            except Exception as e:
                logger.error("Cannot connect to Ollama: %s", e)
                raise
        return self._client

    def _check_model_available(self, model_name: str) -> bool:
        """Check if a model is pulled/available in Ollama."""
        try:
            client = self._get_client()
            models = client.list()
            available = [m.model for m in models.models] if hasattr(models, 'models') else []
            # Also check without tag suffix
            for m in available:
                if m.startswith(model_name):
                    return True
            return False
        except Exception:
            return False

    def analyze(self, prompt: str, force_json: bool = True) -> str:
        """Send a text prompt to the fast text model with JSON format enforcement.

        Args:
            prompt: The prompt to send.
            force_json: If True, use Ollama's format="json" to guarantee JSON output.
        """
        try:
            client = self._get_client()
            model = self._text_model

            # Fallback to vision model if text model not available
            if not self._check_model_available(model):
                logger.warning("Text model %s not available, using %s", model, self._vision_model)
                model = self._vision_model

            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "options": {
                    "temperature": self._temperature,
                    "num_predict": self._max_tokens,
                },
            }
            if force_json:
                kwargs["format"] = "json"

            t0 = time.time()
            response = client.chat(**kwargs)
            elapsed = time.time() - t0
            content = response["message"]["content"]
            logger.debug("Ollama text (%s) took %.1fs, %d chars", model, elapsed, len(content))
            return content

        except Exception as e:
            logger.error("Ollama inference failed: %s", e)
            return f'{{"error": "{e}"}}'

    def analyze_with_image(self, prompt: str, image_path: str, force_json: bool = True) -> str:
        """Send a prompt with an image to the vision model with JSON format enforcement.

        Uses llama3.2-vision (or configured vision model) for multimodal analysis.
        Ollama's format="json" parameter forces valid JSON output.
        """
        try:
            client = self._get_client()

            kwargs = {
                "model": self._vision_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_path],
                    },
                ],
                "options": {
                    "temperature": self._temperature,
                    "num_predict": self._max_tokens,
                },
            }
            if force_json:
                kwargs["format"] = "json"

            t0 = time.time()
            response = client.chat(**kwargs)
            elapsed = time.time() - t0
            content = response["message"]["content"]
            logger.debug(
                "Ollama vision (%s) took %.1fs, %d chars",
                self._vision_model, elapsed, len(content),
            )
            return content

        except Exception as e:
            logger.error("Ollama multimodal failed: %s", e)
            return f'{{"error": "{e}"}}'

    @property
    def name(self) -> str:
        return f"ollama/{self._vision_model}+{self._text_model}"
