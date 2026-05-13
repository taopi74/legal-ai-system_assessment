# legal-ai-system

Minimal end-to-end Legal AI assessment project scaffold.

## Setup

1. Create and activate a virtual environment.
2. Install deps:
   - `pip install -r requirements.txt`
3. Add your key in `.env`:
   - `GEMINI_API_KEY=...`
4. Run API:
   - `uvicorn src.api:app --reload`

## Project Flow

1. Upload/process document (`/upload`)
2. Retrieve evidence (`/retrieve/{doc_id}`)
3. Generate grounded draft (`/draft/{doc_id}`)
4. Save operator edit + learn pattern (`/edit/{doc_id}`)

## Notes

- This is a practical starter setup for the assessment.
- Replace mock parts with production-grade OCR/chunking/parsing as needed.
