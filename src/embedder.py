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
    def _env_int(primary_key: str, alias_key: str, default: int) -> int:
        raw = os.getenv(primary_key) or os.getenv(alias_key)
        if raw is None:
            return default
        try:
            return max(1, int(raw))
        except ValueError:
            return default

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        if not text:
            return []
        words = text.split()
        if not words:
            return []
        chunks: List[str] = []
        start = 0
        while start < len(words):
            end = min(len(words), start + chunk_size)
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = max(0, end - overlap)
        return chunks

    def _chunk_pages(self, pages: List[Dict[str, Any]], chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for page in pages:
            page_number = page.get("page_number")
            for chunk in self.chunk_text(page.get("raw_text", ""), chunk_size=chunk_size, overlap=overlap):
                out.append({"page_number": page_number, "chunk_text": chunk})
        return out

    def index_document(self, doc_id: str, text: str, pages: List[Dict[str, Any]] | None = None) -> Dict[str, int]:
        chunk_size = self._env_int("CHUNK_SIZE", "TOKEN_CHUNK_SIZE", 500)
        chunk_overlap = self._env_int("CHUNK_OVERLAP", "TOKEN_CHUNK_OVERLAP", 50)
        page_chunks = self._chunk_pages(pages or [], chunk_size=chunk_size, overlap=chunk_overlap)
        if not page_chunks and text:
            page_chunks = [{"page_number": None, "chunk_text": c} for c in self.chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)]
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
