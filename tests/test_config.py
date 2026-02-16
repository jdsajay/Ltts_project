"""Tests for the configuration module."""

import os
from pathlib import Path

import pytest


def test_settings_loads():
    """Settings singleton loads without error."""
    from label_compliance.config import get_settings

    s = get_settings()
    assert s is not None
    assert s.paths.standards_dir is not None


def test_settings_defaults():
    """Default values are sensible."""
    from label_compliance.config import get_settings

    s = get_settings()
    assert s.document.render_dpi >= 150
    assert 0.0 < s.compliance.semantic_threshold < 1.0


def test_ensure_dirs(tmp_path, monkeypatch):
    """ensure_dirs creates output directories."""
    from label_compliance.config import get_settings

    s = get_settings()
    # Override output dir to a temp path
    s.paths.output_dir = tmp_path / "out"
    s.paths.redline_dir = tmp_path / "out" / "redlines"
    s.paths.report_dir = tmp_path / "out" / "reports"
    s.paths.log_dir = tmp_path / "out" / "logs"
    s.paths.knowledge_base_dir = tmp_path / "kb"

    s.ensure_dirs()
    assert Path(s.paths.output_dir).exists()
    assert Path(s.paths.redline_dir).exists()
