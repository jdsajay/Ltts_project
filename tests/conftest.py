"""Pytest configuration and shared fixtures."""

import os
import sys
from pathlib import Path

import pytest

# Add project root and src to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Set config path for tests
os.environ.setdefault("LC_CONFIG_DIR", str(ROOT / "config"))


@pytest.fixture
def project_root():
    return ROOT


@pytest.fixture
def sample_pdfs(project_root):
    """Return list of sample label PDFs (if present)."""
    labels_dir = project_root / "data" / "labels"
    if labels_dir.exists():
        return sorted(labels_dir.glob("*.pdf"))
    return []
