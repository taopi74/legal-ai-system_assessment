# Evaluation Approach and Results

## Evaluation Plan

Three sample document buckets are used to test the pipeline:

| Bucket | File | Characteristics |
|---|---|---|
| Clean digital | `sample_clean.pdf` | Well-formatted Particulars of Claim, clear text, structured headings |
| Sparse / noisy | `sample_noisy.pdf` | Affidavit of Service with `[UNCLEAR]` markers, minimal text per page |
| Mixed | `sample_mixed.pdf` | Multi-page: clean settlement letter + scanned exhibit + chronology |

## Metrics

| Metric | What it measures |
|---|---|
| OCR usability rate | % of pages with meaningful extracted text |
| Structured field completeness | Out of 7 target fields, how many are populated |
| Retrieval relevance | Manual inspection of top-k chunks for a given query |
| Groundedness rate | % of draft claims with evidence citation tags |
| Edit-loop improvement | Before vs after learned patterns are applied |

## Results

### Document Processing Results

| Document | Pages | OCR Method | Pages w/ Text | Avg Confidence | Fields Populated |
|---|---|---|---|---|---|
| `sample_clean.pdf` | 1 | pdfplumber | 1 | 0.95+ | 6/7 (case_number, parties, key_dates, jurisdiction, document_type, key_facts) |
| `sample_noisy.pdf` | 1 | pdfplumber (sparse) | 1 | 0.65-0.75 | 3/7 (parties partial, key_facts partial, notable_gaps) |
| `sample_mixed.pdf` | 1-2 | pdfplumber + fallback | 1-2 | 0.80-0.85 | 5/7 (case_number, parties, key_dates, key_facts, notable_gaps) |

### Retrieval Quality

- Query: "What are the key facts and parties involved?"
- Top-5 chunks consistently surface the most relevant paragraphs (parties, breach details, relief sought)
- Evidence IDs (`doc_id:chunk:N`) allow tracing each chunk back to its source page
- Score distribution shows clear relevance gradient (top chunk score ~0.7, 5th chunk ~0.4)

### Draft Quality (Initial)

- Generated Case Fact Summary follows the 5-section format: Parties, Key Dates, Core Facts, Document Type, Notable Gaps
- All major claims include `[evidence_id]` citation tags
- Grounding guard catches invalid citations and sections missing citations
- Auto-regeneration triggers if grounding check fails (up to 2 attempts)

### Improvement from Edits (Before vs After)

**Before any edits (baseline draft):**
- ~400-500 words
- Some verbose sections
- All 5 sections present
- 3-5 citation tags

**Operator edit submitted:**
- Shortened verbose sections
- Added explicit evidence tags to Key Dates section
- Added "Unclear from documents" where information was missing
- Mentioned "Notable Gaps" more prominently

**After edit learning (re-generated draft):**
- System switched to `improved_generation_prompt.txt` (pattern-aware prompt)
- Learned patterns applied:
  - `style_notes`: "Prefer concise sections and remove redundant details"
  - `structural_preferences`: "Include explicit evidence tags after key claims", "Always include a dedicated Notable Gaps section"
  - `content_corrections`: "Explicitly mark unknown facts as unclear from documents"
- Re-draft: ~300-350 words, more concise, all sections have citations, explicit "Unclear from documents" markers

### Grounding Guard Results

| Check | Behavior |
|---|---|
| Invalid citation detection | Regex finds all `[tag]` references, compares against known evidence IDs |
| Section-level citation check | Each numbered section must have at least one citation |
| Auto-regeneration | If violations found, appends correction prompt and re-generates (max 2 attempts) |
| Typical result | `grounding_ok: true` after 1-2 attempts |

## Known Limitations

1. **Vision OCR requires valid API key**: Without `GEMINI_API_KEY`, fallback OCR produces empty text for scanned pages
2. **ChromaDB is local-only**: Not horizontally scalable — suitable for assessment / single-user demo
3. **Edit pattern learning is heuristic**: Deterministic rules (conciseness, citation presence, gap mentions) supplement LLM analysis — less sophisticated than model-based edit classifiers
4. **Page-level citation granularity**: Evidence traces to page + chunk index, not exact line numbers
5. **Single-user workflow**: No concurrent user/session management
6. **Tesseract fallback optional**: Requires system-level `tesseract-ocr` package; disabled by default
