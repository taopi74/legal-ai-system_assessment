from __future__ import annotations

import os
from typing import List

import google.generativeai as genai
from chromadb.api.types import EmbeddingFunction


class GoogleEmbeddingFunction(EmbeddingFunction):
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
        genai.configure(api_key=api_key)

    def __call__(self, input: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in input:
            response = genai.embed_content(model=self.model, content=text, task_type="retrieval_document")
            vectors.append(response.get("embedding", []))
        return vectors
