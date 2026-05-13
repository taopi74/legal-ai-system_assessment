# System Architecture

## End-to-End Flow

1. **Document Ingestion** (`/upload`)
2. **OCR + Text Extraction**
   - Primary: `pdfplumber`
   - Fallback: Gemini Vision OCR for low-text pages
3. **Structured Extraction**
   - JSON fields for downstream retrieval/drafting
4. **Chunking + Embedding Store**
   - ChromaDB collection with chunk metadata and citation ids
5. **Grounded Retrieval** (`/retrieve/{doc_id}`)
   - Top-k chunk retrieval with score and evidence metadata
6. **Draft Generation** (`/draft/{doc_id}`)
   - Prompt-constrained to evidence only
   - Citation-friendly output + evidence map
7. **Feedback Learning** (`/edit/{doc_id}`)
   - Capture original vs edited draft
   - Learn reusable writing preferences

## Key Design Choices

- Threaded OCR fallback for practical speed on noisy PDFs
- Explicit evidence ids (`doc_id:chunk:i`) for inspectable grounding
- Lightweight local vector store for fast setup and demoability
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
