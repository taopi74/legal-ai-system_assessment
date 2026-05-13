# legal-ai-system-assessment

Assessment-oriented Legal AI system for messy document processing, grounded retrieval, draft generation, and improvement from edits.

## Features Implemented

- OCR pipeline with fallback:
  - `pdfplumber` first
  - Gemini Vision OCR fallback for low-text pages
- Structured field extraction (`case_number`, `parties`, `key_dates`, etc.)
- Chunking + vector indexing with ChromaDB
- Google `text-embedding-004` embedding integration
- Grounded retrieval with evidence ids and scores
- Draft generation constrained by retrieved evidence
- Citation-aware draft output and evidence map endpoint
- Operator edit capture with reusable pattern learning
- Document management endpoints (list, inspect, delete by `doc_id`)
- Input validation for retrieval/draft request payloads
- Prompt templates loaded from `prompts/*.txt`
- Basic request-id tracing, optional API-key auth, and rate limiting
- Token-aware chunking (`CHUNK_SIZE`/`CHUNK_OVERLAP`)
- Optional tesseract OCR fallback via feature flag
- Grounding guard with section-wise citation checks and optional auto-regeneration

## Setup

1. Create and activate virtual env
2. Install packages:
   - `pip install -r requirements.txt`
3. Fill `.env`:
   - `GEMINI_API_KEY=...`
4. Run server:
   - `uvicorn src.api:app --reload`

## Architecture Layout

- `src/api.py`: app wiring only (mounts, middleware registration, router include)
- `src/routers/`: domain routers
  - `system.py`: health, upload, review ui route
  - `drafts.py`: retrieve, draft generation, evidence map
  - `feedback.py`: edit capture, pattern read/reset
  - `documents.py`: document list/get/delete
- `src/app_state.py`: shared runtime services and path state
- `src/middleware.py`: API-key auth, rate limit, request-id, latency logging
- `web/`: frontend assets for `/review`
- `prompts/`: external prompt templates

## API Endpoints

- `GET /health`
- `POST /upload` (pdf -> OCR/extraction/indexing)
- `POST /retrieve/{doc_id}`
- `POST /draft/{doc_id}`
- `GET /draft/{doc_id}/evidence-map?query=...`
- `POST /edit/{doc_id}`
- `GET /patterns`
- `POST /reset-patterns`
- `GET /documents`
- `GET /documents/{doc_id}`
- `DELETE /documents/{doc_id}`
- `GET /review` (simple operator review UI)

## Quick Flow

1. Upload PDF
2. Retrieve relevant passages for a task query
3. Generate grounded case-fact summary with citations
4. Submit edited draft
5. Re-run draft to see learned preferences applied

## Runbook

1. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and fill required API keys
4. `uvicorn src.api:app --reload`
5. Open [http://127.0.0.1:8000/review](http://127.0.0.1:8000/review)
6. Upload a pdf via API/docs, then generate+edit drafts in review UI

## Environment Matrix

- **Provider**
  - `LLM_PROVIDER=gemini|claude|openai`
  - `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`
- **Retrieval and chunking**
  - `TOP_K` or `TOP_K_CHUNKS`
  - `CHUNK_SIZE` and `CHUNK_OVERLAP`
- **OCR**
  - `OCR_MAX_WORKERS` or `MAX_THREADS`
  - `ENABLE_TESSERACT_FALLBACK=true|false`
  - `TESSERACT_LANG=eng` (or installed language code)
- **Grounding**
  - `GROUNDING_AUTO_REGENERATE=true|false`
  - `GROUNDING_MAX_ATTEMPTS=2`
- **Ops/security**
  - `RATE_LIMIT_PER_MINUTE`
  - `BASIC_AUTH_API_KEY`

## Troubleshooting

- **`/health` shows `llm_configured=false`**: set API key for active provider.
- **OCR fallback still weak**: enable tesseract and ensure system package is installed.
- **Review UI not loading**: ensure network access for React CDN or migrate to bundled frontend.
- **Frequent 429 responses**: increase `RATE_LIMIT_PER_MINUTE` for local testing.
- **Grounding warnings persist**: increase `GROUNDING_MAX_ATTEMPTS` or tighten prompt wording.

## Additional Docs

- `architecture.md`
- `assumptions_tradeoffs.md`
- `evaluation.md`
