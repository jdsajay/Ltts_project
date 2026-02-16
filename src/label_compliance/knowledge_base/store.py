"""
Knowledge Store (ChromaDB)
===========================
Stores ISO requirements as embeddings in a local ChromaDB
vector database for fast semantic search.
"""

from __future__ import annotations

import json
from pathlib import Path

import chromadb

from label_compliance.config import get_settings
from label_compliance.knowledge_base.embeddings import embed_texts
from label_compliance.utils.helpers import chunk_text
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


class KnowledgeStore:
    """Wraps ChromaDB for ISO requirement storage and retrieval."""

    def __init__(self) -> None:
        settings = get_settings()
        db_path = settings.paths.knowledge_base_dir / "chromadb"
        db_path.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(db_path))
        self._collection = self._client.get_or_create_collection(
            name=settings.kb.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB collection '%s' — %d documents",
            settings.kb.collection_name,
            self._collection.count(),
        )

    @property
    def count(self) -> int:
        return self._collection.count()

    def index_knowledge_base(self, kb_path: Path) -> int:
        """
        Index a knowledge base JSON file into ChromaDB.
        Each requirement and section body is chunked, embedded, and stored.
        """
        settings = get_settings()
        kb = json.loads(kb_path.read_text(encoding="utf-8"))
        iso_id = kb["iso_id"]

        documents: list[str] = []
        metadatas: list[dict] = []
        ids: list[str] = []

        # Index every requirement
        for i, req in enumerate(kb.get("requirements", [])):
            doc_id = f"{iso_id}__req__{i}"
            text = f"[{req['section']} {req['section_title']}] {req['text']}"
            documents.append(text)
            metadatas.append({
                "iso_id": iso_id,
                "section": req["section"],
                "section_title": req["section_title"],
                "type": req["type"],
                "source": "requirement",
            })
            ids.append(doc_id)

        # Index section bodies (chunked)
        for sec in kb.get("sections", []):
            body = sec.get("body", "")
            if len(body) < 30:
                continue
            chunks = chunk_text(body, settings.kb.chunk_size, settings.kb.chunk_overlap)
            for j, chunk in enumerate(chunks):
                doc_id = f"{iso_id}__sec_{sec['number']}__{j}"
                text = f"[{sec['number']} {sec['title']}] {chunk}"
                documents.append(text)
                metadatas.append({
                    "iso_id": iso_id,
                    "section": sec["number"],
                    "section_title": sec["title"],
                    "type": "section_body",
                    "source": "section",
                })
                ids.append(doc_id)

        if not documents:
            logger.warning("No documents to index from %s", kb_path.name)
            return 0

        # Embed and upsert in batches
        batch_size = 100
        total = 0
        for start in range(0, len(documents), batch_size):
            end = start + batch_size
            batch_docs = documents[start:end]
            batch_meta = metadatas[start:end]
            batch_ids = ids[start:end]

            embeddings = embed_texts(batch_docs)
            self._collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
                embeddings=embeddings,
            )
            total += len(batch_ids)

        logger.info("Indexed %d documents from %s", total, iso_id)
        return total

    def search(
        self,
        query: str,
        n_results: int = 10,
        iso_filter: str | None = None,
    ) -> list[dict]:
        """
        Semantic search for requirements matching a query.

        Returns list of {document, metadata, distance}.
        """
        from label_compliance.knowledge_base.embeddings import embed_single

        query_embedding = embed_single(query)

        where = {"iso_id": iso_filter} if iso_filter else None

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "similarity": 1 - results["distances"][0][i],  # cosine distance → similarity
            })

        return hits

    def reset(self) -> None:
        """Delete all documents from the collection."""
        settings = get_settings()
        self._client.delete_collection(settings.kb.collection_name)
        self._collection = self._client.create_collection(
            name=settings.kb.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Knowledge store reset.")
