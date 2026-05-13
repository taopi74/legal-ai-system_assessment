# Evaluation Approach and Results

## Evaluation Plan

Use three sample buckets:

1. Clean digital legal PDFs
2. Scanned/noisy PDFs
3. Mixed/partially unclear pages

## Metrics

- OCR usability rate (% pages with meaningful extracted text)
- Structured field completeness
- Retrieval relevance (manual top-k check)
- Groundedness rate (claims with evidence tags)
- Edit-loop improvement (before vs after learned patterns)

## Current Baseline (Starter)

- OCR fallback: implemented (`pdfplumber` -> Gemini Vision)
- Retrieval traceability: implemented (`evidence_id`, score, evidence map)
- Grounded drafting: implemented with citation instruction
- Edit learning loop: implemented with reusable pattern accumulation

## What to Report Before Submission

- At least 2-3 sample docs with extracted JSON snapshots
- One initial draft and one post-edit re-draft comparison
- A short table with metric observations and known limitations
