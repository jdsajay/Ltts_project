"""
Configuration loader.

Loads settings from config/settings.yaml and .env,
merges them, and provides a typed Settings object
accessible everywhere via `get_settings()`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Project root = 2 levels up from src/label_compliance/
ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = ROOT / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"


@dataclass
class PathSettings:
    standards_dir: Path = field(default_factory=lambda: ROOT / "data" / "standards")
    labels_dir: Path = field(default_factory=lambda: ROOT / "data" / "labels")
    knowledge_base_dir: Path = field(default_factory=lambda: ROOT / "data" / "knowledge_base")
    symbol_library_dir: Path = field(default_factory=lambda: ROOT / "data" / "symbol_library")
    output_dir: Path = field(default_factory=lambda: ROOT / "outputs")
    redline_dir: Path = field(default_factory=lambda: ROOT / "outputs" / "redlines")
    report_dir: Path = field(default_factory=lambda: ROOT / "outputs" / "reports")
    log_dir: Path = field(default_factory=lambda: ROOT / "outputs" / "logs")


@dataclass
class KBSettings:
    collection_name: str = "iso_requirements"
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "all-MiniLM-L6-v2"


@dataclass
class DocumentSettings:
    render_dpi: int = 300
    ocr_language: str = "eng"
    ocr_min_confidence: int = 30
    ocr_preprocess: list[str] = field(default_factory=lambda: ["grayscale", "threshold", "denoise"])


@dataclass
class ComplianceSettings:
    rule_files: list[str] = field(default_factory=lambda: ["iso_14607.yaml", "iso_15223.yaml"])
    semantic_threshold: float = 0.65
    score_compliant: float = 0.85
    score_partial: float = 0.50


@dataclass
class RedlineSettings:
    color_pass: tuple[int, int, int] = (0, 180, 0)
    color_fail: tuple[int, int, int] = (220, 20, 20)
    color_partial: tuple[int, int, int] = (255, 165, 0)
    color_info: tuple[int, int, int] = (0, 100, 200)
    font_size: int = 14
    panel_width: int = 500
    output_format: str = "both"  # "pdf", "png", "both"


@dataclass
class AISettings:
    provider: str = "local"  # "local", "openai", "anthropic", "none"
    local_model: str = "llama3.2"
    temperature: float = 0.1
    max_tokens: int = 2000
    enable_reasoning: bool = True


@dataclass
class ProcessingSettings:
    batch_size: int = 50
    max_workers: int = 4
    resume: bool = True


@dataclass
class Settings:
    """Top-level settings object."""

    paths: PathSettings = field(default_factory=PathSettings)
    kb: KBSettings = field(default_factory=KBSettings)
    document: DocumentSettings = field(default_factory=DocumentSettings)
    compliance: ComplianceSettings = field(default_factory=ComplianceSettings)
    redline: RedlineSettings = field(default_factory=RedlineSettings)
    ai: AISettings = field(default_factory=AISettings)
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)
    log_level: str = "INFO"

    def ensure_dirs(self) -> None:
        """Create all output directories if they don't exist."""
        for p in [
            self.paths.output_dir,
            self.paths.redline_dir,
            self.paths.report_dir,
            self.paths.log_dir,
            self.paths.knowledge_base_dir,
        ]:
            p.mkdir(parents=True, exist_ok=True)


# ── Singleton ─────────────────────────────────────────

_settings: Settings | None = None


def _load_yaml() -> dict:
    """Load the YAML config file."""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def get_settings() -> Settings:
    """Get the global Settings instance (lazy-loaded singleton)."""
    global _settings
    if _settings is not None:
        return _settings

    # Load .env
    load_dotenv(ROOT / ".env")

    # Load YAML
    raw = _load_yaml()

    # Build settings from YAML with .env overrides
    paths_raw = raw.get("paths", {})
    paths = PathSettings(**{k: ROOT / v for k, v in paths_raw.items()}) if paths_raw else PathSettings()

    kb_raw = raw.get("knowledge_base", {})
    kb = KBSettings(
        collection_name=kb_raw.get("collection_name", "iso_requirements"),
        chunk_size=kb_raw.get("chunk_size", 500),
        chunk_overlap=kb_raw.get("chunk_overlap", 50),
        embedding_model=os.getenv("EMBEDDING_MODEL", kb_raw.get("embedding_model", "all-MiniLM-L6-v2")),
    )

    doc_raw = raw.get("document", {})
    doc = DocumentSettings(
        render_dpi=int(os.getenv("RENDER_DPI", doc_raw.get("render_dpi", 300))),
        ocr_language=doc_raw.get("ocr_language", "eng"),
        ocr_min_confidence=doc_raw.get("ocr_min_confidence", 30),
        ocr_preprocess=doc_raw.get("ocr_preprocess", ["grayscale", "threshold", "denoise"]),
    )

    comp_raw = raw.get("compliance", {})
    scores = comp_raw.get("score_levels", {})
    compliance = ComplianceSettings(
        rule_files=comp_raw.get("rule_files", ["iso_14607.yaml", "iso_15223.yaml"]),
        semantic_threshold=comp_raw.get("semantic_threshold", 0.65),
        score_compliant=scores.get("compliant", 0.85),
        score_partial=scores.get("partial", 0.50),
    )

    rl_raw = raw.get("redline", {})
    redline = RedlineSettings(
        color_pass=tuple(rl_raw.get("color_pass", [0, 180, 0])),
        color_fail=tuple(rl_raw.get("color_fail", [220, 20, 20])),
        color_partial=tuple(rl_raw.get("color_partial", [255, 165, 0])),
        color_info=tuple(rl_raw.get("color_info", [0, 100, 200])),
        font_size=rl_raw.get("font_size", 14),
        panel_width=rl_raw.get("panel_width", 500),
        output_format=rl_raw.get("output_format", "both"),
    )

    ai_raw = raw.get("ai", {})
    ai = AISettings(
        provider=os.getenv("AI_PROVIDER", ai_raw.get("provider", "local")),
        local_model=os.getenv("OLLAMA_MODEL", ai_raw.get("local_model", "llama3.2")),
        temperature=ai_raw.get("temperature", 0.1),
        max_tokens=ai_raw.get("max_tokens", 2000),
        enable_reasoning=ai_raw.get("enable_reasoning", True),
    )

    proc_raw = raw.get("processing", {})
    processing = ProcessingSettings(
        batch_size=proc_raw.get("batch_size", 50),
        max_workers=int(os.getenv("MAX_WORKERS", proc_raw.get("max_workers", 4))),
        resume=proc_raw.get("resume", True),
    )

    log_raw = raw.get("logging", {})

    _settings = Settings(
        paths=paths,
        kb=kb,
        document=doc,
        compliance=compliance,
        redline=redline,
        ai=ai,
        processing=processing,
        log_level=os.getenv("LOG_LEVEL", log_raw.get("level", "INFO")),
    )

    return _settings


def get_root() -> Path:
    """Get the project root directory."""
    return ROOT
