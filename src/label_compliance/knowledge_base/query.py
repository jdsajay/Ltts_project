"""
Knowledge Base Query Interface
================================
High-level query functions for retrieving requirements,
matching label text against the KB, and computing coverage.
"""

from __future__ import annotations

from label_compliance.knowledge_base.store import KnowledgeStore
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


def query_requirements(
    query_text: str,
    n_results: int = 10,
    iso_filter: str | None = None,
    store: KnowledgeStore | None = None,
) -> list[dict]:
    """
    Find the most relevant ISO requirements for a given text.

    Args:
        query_text: The label text or element description to search for.
        n_results: Number of results to return.
        iso_filter: Restrict to a specific ISO standard.
        store: Existing KnowledgeStore instance (creates one if None).

    Returns:
        List of matching requirement dicts with similarity scores.
    """
    if store is None:
        store = KnowledgeStore()

    hits = store.search(query_text, n_results=n_results, iso_filter=iso_filter)
    logger.debug("Query '%s...' → %d hits", query_text[:50], len(hits))
    return hits


def find_applicable_requirements(
    label_elements: list[str],
    threshold: float = 0.5,
    store: KnowledgeStore | None = None,
) -> dict[str, list[dict]]:
    """
    For each label element, find applicable ISO requirements.

    Returns mapping: element → list of matching requirements.
    """
    if store is None:
        store = KnowledgeStore()

    results = {}
    for element in label_elements:
        hits = store.search(element, n_results=5)
        matching = [h for h in hits if h["similarity"] >= threshold]
        results[element] = matching

    return results
