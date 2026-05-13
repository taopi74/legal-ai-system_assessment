# Assumptions and Tradeoffs

## Assumptions

- Assessment data can be synthetic/mock legal-like documents.
- A single-user workflow is sufficient for demonstration.
- Local ChromaDB persistence is acceptable for take-home scope.

## Tradeoffs

- **Gemini Vision fallback** improves noisy-page extraction but adds API dependency and cost.
- **ChromaDB local** enables fast setup but is not horizontally scalable like managed vector DBs.
- **Heuristic feedback learning** is deterministic and explainable, but less sophisticated than model-based edit classifiers.
- **Page hint metadata** is used for evidence traceability; exact line-level citation requires richer page-chunk alignment.
