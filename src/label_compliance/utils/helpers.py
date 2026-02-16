"""
Shared helper functions.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


def safe_filename(name: str) -> str:
    """Convert an arbitrary string to a filesystem-safe filename."""
    return re.sub(r"[^\w\-]", "_", name).strip("_")


def file_hash(path: Path, algo: str = "sha256") -> str:
    """Compute hash of a file for cache invalidation."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for embedding."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def find_pdfs(directory: Path, pattern: str = "*.pdf") -> list[Path]:
    """Recursively find all PDFs in a directory."""
    return sorted(directory.rglob(pattern))
