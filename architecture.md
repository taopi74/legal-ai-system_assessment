# System Architecture

## End-to-End Pipeline

```
PDF Upload ──► OCR / Text Extraction ──► Structured Field Extraction
                    │                              │
                    ▼                              ▼
              Page-level text              JSON fields (parties,
              with confidence              dates, jurisdiction, etc.)
                    │
                    ▼
           Chunking + Embedding ──► ChromaDB Vector Store
                                            │
                                            ▼
           Query ──────────────► Top-K Retrieval with scores
                                            │
                                            ▼
                                  Grounded Draft Generation
                                  (citation-constrained)
                                            │
                                            ▼
                                   Grounding Guard Check
                                   (invalid citations?
                                    missing section cites?)
                                            │
                                    ┌───────┴───────┐
                                    │ PASS          │ FAIL
                                    ▼               ▼
                              Return draft    Auto-regenerate
                                              (max N attempts)
                                                    │
                                                    ▼
                                              Return draft
                                                    │
                                                    ▼
                                            Operator Review UI
                                            (edit + submit)
                                                    │
                                                    ▼
                                          Edit Capture + Diff
                                                    │
                                                    ▼
                                        LLM Pattern Analysis
                                        + Heuristic Rules
                                                    │
                                                    ▼
                                        learned_patterns.json
                                        (applied to next draft)
```

## Layers

| # | Layer | File(s) | Responsibility |
|---|---|---|---|
| 1 | Document Processing | `document_processor.py` | OCR with pdfplumber, Gemini Vision fallback, optional Tesseract |
| 2 | Structured Extraction | `document_processor.py` | LLM-based JSON field extraction (case_number, parties, dates, etc.) |
| 3 | Embedding Store | `embedder.py`, `embeddings.py` | Token-aware chunking, Google text-embedding-004, ChromaDB upsert |
| 4 | Retrieval | `retriever.py` | Top-k evidence fetch with scores, evidence map builder |
| 5 | Draft Generation | `draft_generator.py` | Grounded summary with citations, grounding guard, auto-regeneration |
| 6 | Feedback Loop | `feedback_loop.py` | Edit capture, LLM diff analysis, heuristic pattern detection, JSON/SQLite |
| 7 | LLM Abstraction | `llm_provider.py` | Pluggable: Gemini, Claude, OpenAI with retry/timeout/backoff |
| 8 | Prompt Management | `prompt_loader.py`, `prompts/*.txt` | External templates, loaded at runtime, easy to edit |
| 9 | API Orchestration | `api.py`, `routers/` | FastAPI with domain-separated routers |
| 10 | Middleware | `middleware.py` | Auth, rate limiting, request-ID tracing, latency logging |
| 11 | Frontend | `web/` | React operator review UI served as static files |

## Design Principles

- **Grounded generation only** — no unsupported claims; grounding guard rejects violations
- **Pluggable LLM provider** — swap between Gemini/Claude/OpenAI via env var
- **Improvement from edits** — dual strategy: LLM-analyzed patterns + heuristic rules
- **Prompt routing** — baseline prompt for first draft, improved prompt once patterns exist
- **Evidence traceability** — `doc_id:chunk:N` IDs, page hints, evidence map endpoint
- **Local-first storage** — ChromaDB + JSON files for quick setup and demoability
- **Separation of concerns** — routers, services, middleware, prompts all isolated
