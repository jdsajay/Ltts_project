"""Redline subpackage — annotated output generation."""

from label_compliance.redline.annotator import annotate_label
from label_compliance.redline.report import generate_report

__all__ = ["annotate_label", "generate_report"]
