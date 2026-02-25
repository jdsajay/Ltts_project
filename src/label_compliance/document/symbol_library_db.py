"""
Symbol Library Database
========================
Loads the symbol library from the extracted JSON database
(originally from the Symbol Library Export Excel file).

Provides lookup functions for:
- Finding required symbols by classification, standard reference, or text
- Getting expected package text for each symbol
- Getting reference thumbnail images for visual comparison
- Matching detected symbols/text against the library
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

DB_FILENAME = "symbol_library.json"
IMAGES_SUBDIR = "images"


@dataclass
class SymbolEntry:
    """One symbol from the library."""

    row: int
    name: str
    classification: str  # "Standard", "Proprietary - Ethicon", "Product Graphic", etc.
    status: str  # "Active", "Work In Progress"
    pkg_text: str  # expected text on package artwork
    ifu_text: str  # expected text in IFU legend
    sme_function: str
    rev_history: str
    regulations: str  # regulation references (ISO 15223, etc.)
    notes: str
    thumb_file_ref: str  # original thumbnail filename in Excel
    std_thumb_file_ref: str  # standard harmonized thumbnail filename
    thumb_images: list[str] = field(default_factory=list)  # extracted image filenames
    std_thumb_images: list[str] = field(default_factory=list)

    @property
    def is_standard(self) -> bool:
        return self.classification == "Standard"

    @property
    def is_iso_15223(self) -> bool:
        return "ISO 15223" in self.regulations or "15223" in self.regulations

    @property
    def is_active(self) -> bool:
        return self.status == "Active"

    @property
    def search_text(self) -> str:
        """Combined text for fuzzy matching."""
        return f"{self.name} {self.pkg_text} {self.ifu_text}".lower()

    @property
    def regulation_ids(self) -> list[str]:
        """Extract regulation IDs from the regulations field."""
        ids = []
        if not self.regulations:
            return ids
        # Match patterns like "ISO 15223", "ISO 7000", "IEC 60417"
        for m in re.finditer(r"(ISO|IEC|EN|BS)\s*[\d\-]+", self.regulations):
            ids.append(m.group(0).strip())
        return ids

    def get_thumb_path(self, library_dir: Path) -> Optional[Path]:
        """Get the path to the extracted thumbnail image."""
        img_dir = library_dir / IMAGES_SUBDIR
        for fname in self.thumb_images:
            p = img_dir / fname
            if p.exists():
                return p
        return None

    def get_std_thumb_path(self, library_dir: Path) -> Optional[Path]:
        """Get the path to the standard harmonized thumbnail."""
        img_dir = library_dir / IMAGES_SUBDIR
        for fname in self.std_thumb_images:
            p = img_dir / fname
            if p.exists():
                return p
        # Fallback to regular thumb
        return self.get_thumb_path(library_dir)


class SymbolLibrary:
    """
    In-memory symbol library database.

    Loaded from the extracted JSON file (data/symbol_library/symbol_library.json).
    Provides lookup and search functions.
    """

    def __init__(self, db_path: Path | None = None):
        settings = get_settings()
        self._library_dir = settings.paths.symbol_library_dir
        self._db_path = db_path or (self._library_dir / DB_FILENAME)
        self._symbols: list[SymbolEntry] = []
        self._by_pkg_text: dict[str, list[SymbolEntry]] = {}
        self._by_classification: dict[str, list[SymbolEntry]] = {}
        self._loaded = False

    def load(self) -> None:
        """Load the symbol library from JSON."""
        if self._loaded:
            return

        if not self._db_path.exists():
            logger.warning(
                "Symbol library not found at %s. "
                "Run `python scripts/extract_symbol_library.py` to create it.",
                self._db_path,
            )
            self._loaded = True
            return

        with open(self._db_path) as f:
            data = json.load(f)

        for entry in data.get("symbols", []):
            sym = SymbolEntry(
                row=entry.get("row", 0),
                name=entry.get("name", ""),
                classification=entry.get("classification", ""),
                status=entry.get("status", ""),
                pkg_text=entry.get("pkg_text", ""),
                ifu_text=entry.get("ifu_text", ""),
                sme_function=entry.get("sme_function", ""),
                rev_history=entry.get("rev_history", ""),
                regulations=entry.get("regulations", ""),
                notes=entry.get("notes", ""),
                thumb_file_ref=entry.get("thumb_file_ref", ""),
                std_thumb_file_ref=entry.get("std_thumb_file_ref", ""),
                thumb_images=entry.get("thumb_images", []),
                std_thumb_images=entry.get("std_thumb_images", []),
            )
            self._symbols.append(sym)

            # Index by package text (lowered)
            key = sym.pkg_text.strip().lower()
            if key:
                self._by_pkg_text.setdefault(key, []).append(sym)

            # Index by classification
            self._by_classification.setdefault(sym.classification, []).append(sym)

        self._loaded = True
        logger.info(
            "Symbol library loaded: %d symbols (%d standard, %d ISO 15223)",
            len(self._symbols),
            len(self.get_standard_symbols()),
            len(self.get_iso15223_symbols()),
        )

    @property
    def symbols(self) -> list[SymbolEntry]:
        self.load()
        return self._symbols

    def get_standard_symbols(self) -> list[SymbolEntry]:
        """Get all 'Standard' classification symbols."""
        self.load()
        return [s for s in self._symbols if s.is_standard and s.is_active]

    def get_iso15223_symbols(self) -> list[SymbolEntry]:
        """Get all symbols referencing ISO 15223."""
        self.load()
        return [s for s in self._symbols if s.is_iso_15223 and s.is_active]

    def get_by_classification(self, classification: str) -> list[SymbolEntry]:
        """Get symbols by classification type."""
        self.load()
        return self._by_classification.get(classification, [])

    def find_by_text(self, text: str, threshold: float = 0.7) -> list[tuple[SymbolEntry, float]]:
        """
        Find symbols whose pkg_text or ifu_text matches the given text.
        Returns list of (symbol, score) tuples sorted by score descending.
        """
        self.load()
        text_lower = text.strip().lower()
        if not text_lower:
            return []

        results: list[tuple[SymbolEntry, float]] = []
        for sym in self._symbols:
            if not sym.is_active:
                continue
            score = _text_similarity(text_lower, sym.pkg_text.lower())
            ifu_score = _text_similarity(text_lower, sym.ifu_text.lower())
            best = max(score, ifu_score)
            if best >= threshold:
                results.append((sym, best))

        results.sort(key=lambda x: -x[1])
        return results

    def find_by_keywords(self, keywords: list[str]) -> list[SymbolEntry]:
        """Find symbols containing all given keywords in their text."""
        self.load()
        kw_lower = [k.lower() for k in keywords]
        matches = []
        for sym in self._symbols:
            if not sym.is_active:
                continue
            search = sym.search_text
            if all(k in search for k in kw_lower):
                matches.append(sym)
        return matches

    def find_by_regulation(self, pattern: str) -> list[SymbolEntry]:
        """Find symbols whose regulations field matches the pattern."""
        self.load()
        regex = re.compile(pattern, re.IGNORECASE)
        return [
            s for s in self._symbols
            if s.is_active and regex.search(s.regulations)
        ]

    def get_expected_symbols_for_breast_implant(self) -> list[SymbolEntry]:
        """
        Get the list of symbols expected on a breast implant label
        based on ISO 14607, ISO 15223, and EU MDR requirements.
        """
        self.load()
        keywords_groups = [
            ["manufacturer"],
            ["sterile"],
            ["lot", "batch"],
            ["serial", "number"],
            ["use", "by"],  # expiry
            ["date", "manufacture"],
            ["single", "use"],
            ["do not", "re-use"],
            ["do not", "resterilize"],
            ["caution"],
            ["CE"],  # CE mark
            ["REF"],  # catalog/reference number
            ["unique", "device"],  # UDI
            ["medical", "device"],
            ["implant"],
            ["authorized", "representative"],
        ]

        found = {}
        for kws in keywords_groups:
            for sym in self._symbols:
                if not sym.is_active:
                    continue
                search = sym.search_text
                if all(k.lower() in search for k in kws):
                    if sym.row not in found:
                        found[sym.row] = sym

        return list(found.values())

    @property
    def library_dir(self) -> Path:
        return self._library_dir


def _text_similarity(a: str, b: str) -> float:
    """Simple word overlap similarity score."""
    if not a or not b:
        return 0.0
    words_a = set(re.findall(r'\w+', a.lower()))
    words_b = set(re.findall(r'\w+', b.lower()))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


# ── Singleton ──────────────────────────────────────────
_library_instance: SymbolLibrary | None = None


def get_symbol_library() -> SymbolLibrary:
    """Get or create the singleton SymbolLibrary instance."""
    global _library_instance
    if _library_instance is None:
        _library_instance = SymbolLibrary()
    return _library_instance
