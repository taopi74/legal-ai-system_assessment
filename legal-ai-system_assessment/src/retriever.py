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
        k = top_k or self.top_k
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
            out.append(
                {
                    "chunk_text": doc,
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": distances[i] if i < len(distances) else None,
                }
            )
        return out
