"""
Embedding Engine
=================
Generates vector embeddings using sentence-transformers (free, local).
Supports swapping to OpenAI embeddings via config.
"""

from __future__ import annotations

from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

_model = None


def _get_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        settings = get_settings()
        model_name = settings.kb.embedding_model
        logger.info("Loading embedding model: %s", model_name)
        _model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded (dim=%d)", _model.get_sentence_embedding_dimension())
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts into vectors."""
    model = _get_model()
    # Sanitize: replace None/non-string values with empty string
    clean_texts = [t if isinstance(t, str) else "" for t in texts]
    embeddings = model.encode(clean_texts, show_progress_bar=len(clean_texts) > 100)
    return [e.tolist() for e in embeddings]


def embed_single(text: str) -> list[float]:
    """Embed a single text string."""
    return embed_texts([text])[0]
