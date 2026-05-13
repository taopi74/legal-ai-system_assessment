# Architecture Overview

## Layers

1. **Document Processing**: OCR/text extraction from PDF (`document_processor.py`)
2. **Structured Extraction**: parse key legal fields from text
3. **Embedding Store**: chunk + embed + save vectors in Chroma (`embedder.py`)
4. **Retrieval**: top-k evidence fetch (`retriever.py`)
5. **Draft Generation**: grounded case-fact summary (`draft_generator.py`)
6. **Operator Feedback**: capture edits and learn patterns (`feedback_loop.py`)
7. **API Orchestration**: FastAPI endpoints (`api.py`)

## Design Principles

- Grounded generation only (no unsupported claims)
- Pluggable LLM provider abstraction
- Incremental improvement from operator edits
- Simple local-first storage for quick assessment delivery
