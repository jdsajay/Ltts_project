"""
Rule Loader
=============
Loads compliance rules from config/rules/*.yaml files.
Rules define what to check on each label.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from label_compliance.config import get_settings, get_root
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

_rules_cache: dict[frozenset[str], list[dict]] = {}


def load_rules(rule_files: list[str] | None = None) -> list[dict]:
    """
    Load all compliance rules from YAML files.

    Args:
        rule_files: Specific rule files to load. Defaults to config list.

    Returns:
        Combined list of all rules from all files.
    """
    global _rules_cache

    settings = get_settings()
    rules_dir = get_root() / "config" / "rules"

    if rule_files is None:
        rule_files = settings.compliance.rule_files

    cache_key = frozenset(rule_files)
    if cache_key in _rules_cache:
        return _rules_cache[cache_key]

    all_rules: list[dict] = []

    for filename in rule_files:
        rule_path = rules_dir / filename
        if not rule_path.exists():
            logger.warning("Rule file not found: %s", rule_path)
            continue

        with open(rule_path, "r") as f:
            data = yaml.safe_load(f)

        standard = data.get("standard", filename)
        rules = data.get("rules", [])

        for rule in rules:
            rule["_source_file"] = filename
            rule["_standard"] = standard

        all_rules.extend(rules)
        logger.info("Loaded %d rules from %s (%s)", len(rules), filename, standard)

    _rules_cache[cache_key] = all_rules
    logger.info("Total rules loaded: %d", len(all_rules))
    return all_rules


def get_rules_by_category(category: str) -> list[dict]:
    """Get rules filtered by category (symbol, text, dimension, visual, packaging)."""
    return [r for r in load_rules() if r.get("category") == category]


def get_rules_by_severity(severity: str) -> list[dict]:
    """Get rules filtered by severity (critical, major, minor)."""
    return [r for r in load_rules() if r.get("severity") == severity]


def get_new_2024_rules() -> list[dict]:
    """Get rules that are new in the 2024 edition."""
    return [r for r in load_rules() if r.get("new_in_2024", False)]


def reload_rules() -> list[dict]:
    """Force reload of rules (clears cache)."""
    global _rules_cache
    _rules_cache = {}
    return load_rules()


def resolve_rules_for_label(label_filename: str) -> tuple[list[dict], str]:
    """
    Resolve which rules apply to a specific label based on profiles.

    Profiles are defined in config/settings.yaml under 'profiles'.
    Each profile maps filename glob patterns to specific rule files.
    Labels not matching any profile fall back to compliance.rule_files.

    Args:
        label_filename: The label's filename (e.g., "ARTW-100765708.pdf").

    Returns:
        Tuple of (rules_list, profile_name).
        profile_name is "default" if no profile matched.
    """
    from fnmatch import fnmatch
    from label_compliance.config import get_root

    settings = get_settings()

    # Load profiles from YAML directly (not in Settings dataclass)
    yaml_path = get_root() / "config" / "settings.yaml"
    profiles = {}
    if yaml_path.exists():
        import yaml as _yaml
        with open(yaml_path, "r") as f:
            raw = _yaml.safe_load(f) or {}
        profiles = raw.get("profiles", {})

    # Try to match against profiles
    stem = Path(label_filename).stem
    for profile_name, profile in profiles.items():
        patterns = profile.get("patterns", [])
        for pat in patterns:
            if fnmatch(stem, pat) or fnmatch(label_filename, pat):
                rule_files = profile.get("rule_files", [])
                desc = profile.get("description", profile_name)
                logger.info(
                    "Label '%s' matched profile '%s' (%s) → rules: %s",
                    label_filename, profile_name, desc, rule_files,
                )
                rules = load_rules(rule_files)
                return rules, profile_name

    # No profile matched — use default rule_files
    logger.info(
        "Label '%s' matched no profile — using default rules: %s",
        label_filename, settings.compliance.rule_files,
    )
    return load_rules(), "default"
