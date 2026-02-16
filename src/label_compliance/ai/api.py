"""
OpenAI Provider (API)
======================
Uses OpenAI GPT-4o for multimodal compliance analysis.
Requires OPENAI_API_KEY in .env.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

from label_compliance.ai.base import AIProvider
from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    """API-based AI provider using OpenAI."""

    def __init__(self) -> None:
        settings = get_settings()
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self._temperature = settings.ai.temperature
        self._max_tokens = settings.ai.max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not set. Add it to .env or export OPENAI_API_KEY=sk-..."
                )
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized, model=%s", self._model)
        return self._client

    def analyze(self, prompt: str) -> str:
        """Send a text prompt to OpenAI."""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert in medical device regulatory compliance, "
                            "specifically ISO 14607 (breast implants), ISO 15223-1 (symbols), "
                            "and EU MDR labeling requirements."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI call failed: %s", e)
            return f"[OpenAI error: {e}]"

    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """Send a prompt with an image to GPT-4o (multimodal)."""
        try:
            client = self._get_client()

            # Encode image as base64
            img_data = Path(image_path).read_bytes()
            b64 = base64.b64encode(img_data).decode("utf-8")

            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    },
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI multimodal call failed: %s", e)
            return f"[OpenAI multimodal error: {e}]"

    @property
    def name(self) -> str:
        return f"openai/{self._model}"
