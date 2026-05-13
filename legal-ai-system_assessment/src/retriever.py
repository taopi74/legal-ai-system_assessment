from __future__ import annotations

import os
from typing import Any, Dict, List

import chromadb


class Retriever:
    def __init__(self) -> None:
        chroma_dir = os.getenv("CHROMA_DIR", "./data/chroma")
        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.client.get_or_create_collection("legal_chunks")
        self.top_k = int(os.getenv("TOP_K", "5"))

    def retrieve(self, doc_id: str, query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
        if not query.strip():
            return []
        k = top_k or self.top_k
        if k <= 0:
            return []
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where={"doc_id": doc_id},
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        out: List[Dict[str, Any]] = []
        for i, doc in enumerate(docs):
            distance = distances[i] if i < len(distances) else None
            out.append(
                {
                    "evidence_id": (metas[i] or {}).get("citation_id", f"{doc_id}:chunk:{i}") if i < len(metas) else f"{doc_id}:chunk:{i}",
                    "chunk_text": doc,
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": distance,
                    "score": (1.0 / (1.0 + float(distance))) if distance is not None else None,
                }
            )
        return out

    def build_evidence_map(self, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "evidence_id": item.get("evidence_id"),
                "page_hint": item.get("metadata", {}).get("page_hint", "unknown"),
                "chunk_index": item.get("metadata", {}).get("chunk_index"),
                "score": item.get("score"),
            }
            for item in evidence
        ]
