"""
Centralized logging configuration.

Usage:
    from label_compliance.utils.log import get_logger
    logger = get_logger(__name__)
    logger.info("Processing label %s", label_name)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_configured = False


def setup_logging(level: str = "INFO", log_file: Path | None = None) -> None:
    """Configure logging for the entire application. Call once at startup."""
    global _configured
    if _configured:
        return

    root = logging.getLogger("label_compliance")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(fmt)
    root.addHandler(console)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module. Automatically namespaced under 'label_compliance'."""
    if not name.startswith("label_compliance"):
        name = f"label_compliance.{name}"
    return logging.getLogger(name)
