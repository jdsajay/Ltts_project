"""
"""API Provider (OpenAI-compatible)
======================
Uses any OpenAI-compatible API for multimodal compliance analysis.
Supports OpenAI, xAI/Grok, NVIDIA NIM, Together, Groq, Azure, etc.
Requires API key set in the env var configured by settings.yaml → ai.api_key_env_var.

Advantages over local models:
  - Much higher accuracy for compliance reasoning
  - Native JSON mode (response_format) for guaranteed valid output
  - Superior multimodal vision (label image analysis)
  - Large context windows
"""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path

from label_compliance.ai.base import AIProvider
from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are an expert ISO compliance auditor for medical device labels. "
    "You specialize in ISO 14607 (breast implants), ISO 15223-1 (symbols), "
    "and EU MDR labeling requirements. "
    "Always respond with valid JSON only. No markdown, no extra text."
)


class OpenAIProvider(AIProvider):
    """API-based AI provider using any OpenAI-compatible endpoint.

    Features:
    - JSON mode (response_format) for guaranteed valid JSON output
    - Multimodal vision with high-detail image analysis
    - Works with OpenAI, xAI/Grok, NVIDIA NIM, Together, Groq, Azure
    - Cost tracking via token usage logging
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._model = os.getenv("OPENAI_MODEL", settings.ai.ingestion_model)
        self._temperature = settings.ai.temperature
        self._max_tokens = settings.ai.max_tokens
        self._client = None
        self._total_tokens = 0
        self._total_calls = 0

    def _get_client(self):
        if self._client is None:
            from label_compliance.config import get_ai_client
            self._client = get_ai_client()
            logger.info("API client initialized — model=%s", self._model)
        return self._client

    def analyze(self, prompt: str) -> str:
        """Send a text prompt to GPT-4o with JSON response format.

        Uses response_format=json_object for guaranteed valid JSON,
        matching the behavior of Ollama's format='json'.
        """
        try:
            client = self._get_client()
            t0 = time.time()

            response = client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )

            elapsed = time.time() - t0
            content = response.choices[0].message.content
            usage = response.usage
            self._total_calls += 1
            if usage:
                self._total_tokens += usage.total_tokens
                logger.debug(
                    "OpenAI text took %.1fs — %d tokens (prompt=%d, completion=%d) | total: %d tokens across %d calls",
                    elapsed, usage.total_tokens, usage.prompt_tokens,
                    usage.completion_tokens, self._total_tokens, self._total_calls,
                )
            return content

        except Exception as e:
            logger.error("OpenAI call failed: %s", e)
            return f'{{"error": "{e}"}}'

    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """Send a prompt with an image to GPT-4o (multimodal).

        Uses high-detail mode for accurate label/symbol analysis.
        JSON response format ensures parseable output.
        """
        try:
            client = self._get_client()
            t0 = time.time()

            # Encode image as base64
            img_data = Path(image_path).read_bytes()
            b64 = base64.b64encode(img_data).decode("utf-8")

            # Determine MIME type from extension
            ext = Path(image_path).suffix.lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(
                ext.lstrip("."), "image/png"
            )

            response = client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{b64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    },
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )

            elapsed = time.time() - t0
            content = response.choices[0].message.content
            usage = response.usage
            self._total_calls += 1
            if usage:
                self._total_tokens += usage.total_tokens
                logger.debug(
                    "OpenAI vision took %.1fs — %d tokens | total: %d tokens across %d calls",
                    elapsed, usage.total_tokens, self._total_tokens, self._total_calls,
                )
            return content

        except Exception as e:
            logger.error("OpenAI multimodal call failed: %s", e)
            return f'{{"error": "{e}"}}'

    @property
    def name(self) -> str:
        return f"openai/{self._model}"

    @property
    def name(self) -> str:
        return f"openai/{self._model}"
