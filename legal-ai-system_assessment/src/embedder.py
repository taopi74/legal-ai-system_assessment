from __future__ import annotations

import os
from typing import Any, Dict, List

import chromadb

from src.embeddings import GoogleEmbeddingFunction


class Embedder:
    def __init__(self) -> None:
        chroma_dir = os.getenv("CHROMA_DIR", "./data/chroma")
        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.client.get_or_create_collection(
            "legal_chunks",
            embedding_function=GoogleEmbeddingFunction(),
        )

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

    def _chunk_pages(self, pages: List[Dict[str, Any]], chunk_size: int = 1200, overlap: int = 120) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for page in pages:
            page_number = page.get("page_number")
            for chunk in self.chunk_text(page.get("raw_text", ""), chunk_size=chunk_size, overlap=overlap):
                out.append({"page_number": page_number, "chunk_text": chunk})
        return out

    def index_document(self, doc_id: str, text: str, pages: List[Dict[str, Any]] | None = None) -> Dict[str, int]:
        page_chunks = self._chunk_pages(pages or [])
        if not page_chunks and text:
            page_chunks = [{"page_number": None, "chunk_text": c} for c in self.chunk_text(text)]
        if not page_chunks:
            return {"chunk_count": 0}
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(page_chunks))]
        docs = [item["chunk_text"] for item in page_chunks]
        metadatas = [
            {
                "doc_id": doc_id,
                "chunk_index": i,
                "citation_id": f"{doc_id}:chunk:{i}",
                "page_number": page_chunks[i].get("page_number"),
                "page_hint": str(page_chunks[i].get("page_number") or "unknown"),
                "token_estimate": max(1, len(docs[i]) // 4),
            }
            for i in range(len(page_chunks))
        ]
        self.collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
        return {"chunk_count": len(page_chunks)}

    def delete_document_chunks(self, doc_id: str) -> int:
        existing = self.collection.get(where={"doc_id": doc_id}, include=[])
        ids = existing.get("ids", [])
        if not ids:
            return 0
        self.collection.delete(ids=ids)
        return len(ids)
