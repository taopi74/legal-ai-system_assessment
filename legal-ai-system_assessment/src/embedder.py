from __future__ import annotations

import os
from typing import Any, Dict, List

import chromadb


class Embedder:
    def __init__(self) -> None:
        chroma_dir = os.getenv("CHROMA_DIR", "./data/chroma")
        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.client.get_or_create_collection("legal_chunks")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 120) -> List[str]:
        if not text:
            return []
        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            chunks.append(text[start:end])
            if end == len(text):
                break
            start = max(0, end - overlap)
        return chunks

    def index_document(self, doc_id: str, text: str, pages: List[Dict[str, Any]] | None = None) -> Dict[str, int]:
        chunks = self.chunk_text(text)
        if not chunks:
            return {"chunk_count": 0}
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        source_pages = [p.get("page_number") for p in (pages or []) if p.get("raw_text")]
        page_hint = ",".join(str(x) for x in source_pages[:20]) if source_pages else "unknown"
        metadatas = [
            {
                "doc_id": doc_id,
                "chunk_index": i,
                "citation_id": f"{doc_id}:chunk:{i}",
                "page_hint": page_hint,
                "token_estimate": max(1, len(chunks[i]) // 4),
            }
            for i in range(len(chunks))
        ]
        self.collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
        return {"chunk_count": len(chunks)}
