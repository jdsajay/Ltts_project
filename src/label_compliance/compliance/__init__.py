"""Compliance engine subpackage — rules, matching, scoring, checking."""

from label_compliance.compliance.checker import check_label
from label_compliance.compliance.rules import load_rules

__all__ = ["check_label", "load_rules"]
