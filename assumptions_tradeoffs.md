# Assumptions and Tradeoffs

## Assumptions

- Assessment data uses synthetic/mock legal-like documents (no real confidential data).
- A single-user workflow is sufficient for demonstration scope.
- Local ChromaDB persistence is acceptable for a take-home assessment.
- The Gemini API key is available for OCR fallback and LLM generation.
- Operators review drafts in real-time (no async/queue-based review workflow).
- The "Case Fact Summary" is the chosen draft output format (from the menu of options in the assessment).
  
## Why "Case Fact Summary" was chosen
From the menu of draft types, Case Fact Summary was selected because:
1. It directly maps to the retrieval task — parties, dates, and facts are all retrievable fields
2. It has a clear grounding requirement — every claim must cite source evidence
3. It is the most useful first-pass output for a legal operator reviewing an unfamiliar document

## Why Gemini over Claude/OpenAI
Gemini was chosen as default because it offers Vision OCR + text generation in a single API,
reducing the number of external dependencies for the assessment scope.

## What I would change in production
- Replace ChromaDB with a hosted vector DB (Pinecone/Weaviate) for multi-user support
- Use a dedicated OCR service (AWS Textract) instead of Vision LLM for cost efficiency  
- Replace heuristic pattern learning with a fine-tuned preference model over time
## Tradeoffs

| Decision | Benefit | Cost |
|---|---|---|
| **Gemini Vision OCR fallback** | Handles noisy/scanned pages well | Adds API dependency and per-call cost |
| **ChromaDB local** | Zero-config setup, fast for demos | Not horizontally scalable; single-process |
| **Heuristic feedback learning** | Deterministic, explainable, always fires | Less sophisticated than model-based edit classifiers |
| **LLM-based pattern extraction** | Captures nuanced writing preferences | Requires API call on each edit submission |
| **Dual prompt strategy** | Clean baseline vs. pattern-aware improved | Two prompt files to maintain |
| **JSON + optional SQLite** | Flexible storage, easy inspection | JSON doesn't scale for high-volume edit history |
| **Page hint metadata** | Evidence traceability at page level | Not exact line-level citation |
| **External prompt templates** | Easy to iterate without code changes | Prompt drift risk if templates get out of sync |
| **React via CDN** | No build step, instant setup | Depends on network for React/Babel CDN |
