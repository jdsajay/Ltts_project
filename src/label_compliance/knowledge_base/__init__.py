"""Knowledge base subpackage — ingest ISO standards, embed, store, query."""

from label_compliance.knowledge_base.ingester import ingest_standard
from label_compliance.knowledge_base.store import KnowledgeStore
from label_compliance.knowledge_base.query import query_requirements

__all__ = ["ingest_standard", "KnowledgeStore", "query_requirements"]
