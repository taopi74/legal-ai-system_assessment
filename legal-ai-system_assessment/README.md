# legal-ai-system-assessment

Assessment-oriented Legal AI system for messy document processing, grounded retrieval, draft generation, and improvement from edits.

## Features Implemented

- OCR pipeline with fallback:
  - `pdfplumber` first
  - Gemini Vision OCR fallback for low-text pages
- Structured field extraction (`case_number`, `parties`, `key_dates`, etc.)
- Chunking + vector indexing with ChromaDB
- Grounded retrieval with evidence ids and scores
- Draft generation constrained by retrieved evidence
- Citation-aware draft output and evidence map endpoint
- Operator edit capture with reusable pattern learning

## Setup

1. Create and activate virtual env
2. Install packages:
   - `pip install -r requirements.txt`
3. Fill `.env`:
   - `GEMINI_API_KEY=...`
4. Run server:
   - `uvicorn src.api:app --reload`

## API Endpoints

- `GET /health`
- `POST /upload` (pdf -> OCR/extraction/indexing)
- `POST /retrieve/{doc_id}`
- `POST /draft/{doc_id}`
- `GET /draft/{doc_id}/evidence-map?query=...`
- `POST /edit/{doc_id}`
- `GET /patterns`

## Quick Flow

1. Upload PDF
2. Retrieve relevant passages for a task query
3. Generate grounded case-fact summary with citations
4. Submit edited draft
5. Re-run draft to see learned preferences applied

## Additional Docs

- `architecture.md`
- `assumptions_tradeoffs.md`
- `evaluation.md`
