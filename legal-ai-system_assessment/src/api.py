from __future__ import annotations

import json
import logging
import os
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.document_processor import DocumentProcessor
from src.draft_generator import DraftGenerator
from src.embedder import Embedder
from src.feedback_loop import FeedbackLoop
from src.retriever import Retriever

app = FastAPI(title="Legal AI System")
logger = logging.getLogger("legal-ai")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.setLevel(logging.INFO)

uploads_dir = Path("data/sample_inputs")
uploads_dir.mkdir(parents=True, exist_ok=True)

processor = DocumentProcessor()
embedder = Embedder()
retriever = Retriever()
drafter = DraftGenerator()
feedback = FeedbackLoop()
request_counters: dict[str, dict[str, int]] = defaultdict(dict)


@app.middleware("http")
async def security_and_logging(request: Request, call_next):
    request_id = str(uuid.uuid4())
    now_bucket = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M")
    client_ip = request.client.host if request.client else "unknown"
    counter_key = f"{client_ip}:{now_bucket}"

    api_key = os.getenv("BASIC_AUTH_API_KEY", "")
    if api_key:
        provided = request.headers.get("x-api-key", "")
        if provided != api_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    current = request_counters[now_bucket].get(counter_key, 0)
    if current >= limit:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    request_counters[now_bucket][counter_key] = current + 1

    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "client_ip": client_ip,
            }
        )
    )
    return response


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)


class EditRequest(BaseModel):
    original_draft: str
    edited_draft: str


class ResetPatternsResponse(BaseModel):
    style_notes: list[str]
    content_corrections: list[str]
    structural_preferences: list[str]


def _load_processed_doc(doc_id: str) -> dict:
    extracted_file = Path("data/extracted") / f"{doc_id}.json"
    if not extracted_file.exists():
        raise HTTPException(status_code=404, detail="Document not found.")
    return json.loads(extracted_file.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF is supported.")
    doc_id = str(uuid.uuid4())
    out_path = uploads_dir / f"{doc_id}.pdf"
    out_path.write_bytes(await file.read())

    processed = processor.process_pdf(str(out_path), doc_id)
    embed_stats = embedder.index_document(
        doc_id,
        processed.get("merged_text", ""),
        pages=processed.get("pages", []),
    )
    return {
        "doc_id": doc_id,
        "embed": embed_stats,
        "status": "processed",
        "extraction_quality": processed.get("extraction_quality", {}),
        "warnings": processed.get("extraction_warnings", []),
    }


@app.post("/retrieve/{doc_id}")
def retrieve(doc_id: str, payload: RetrieveRequest) -> dict:
    evidence = retriever.retrieve(doc_id=doc_id, query=payload.query, top_k=payload.top_k)
    return {"doc_id": doc_id, "query": payload.query, "evidence": evidence}


@app.post("/draft/{doc_id}")
def draft(doc_id: str, payload: RetrieveRequest) -> dict:
    processed = _load_processed_doc(doc_id)
    evidence = retriever.retrieve(doc_id=doc_id, query=payload.query, top_k=payload.top_k)
    draft_payload = drafter.generate_grounded(processed.get("structured_fields", {}), evidence)
    return {
        "doc_id": doc_id,
        "draft": draft_payload["draft_text"],
        "citations": draft_payload["citations"],
        "evidence_count": draft_payload["evidence_count"],
        "evidence_map": retriever.build_evidence_map(evidence),
        "warning": "No evidence found for this query." if not evidence else None,
        "invalid_citations": draft_payload["invalid_citations"],
        "grounding_ok": draft_payload["grounding_ok"],
    }


@app.get("/draft/{doc_id}/evidence-map")
def draft_evidence_map(doc_id: str, query: str, top_k: int | None = None) -> dict:
    evidence = retriever.retrieve(doc_id=doc_id, query=query, top_k=top_k)
    return {"doc_id": doc_id, "query": query, "evidence_map": retriever.build_evidence_map(evidence)}


@app.post("/edit/{doc_id}")
def edit(doc_id: str, payload: EditRequest) -> dict:
    result = feedback.save_edit(
        doc_id=doc_id,
        original_text=payload.original_draft,
        edited_text=payload.edited_draft,
    )
    return {"doc_id": doc_id, **result, "patterns": feedback.get_patterns()}


@app.get("/patterns")
def patterns() -> dict:
    return feedback.get_patterns()


@app.post("/reset-patterns", response_model=ResetPatternsResponse)
def reset_patterns() -> dict:
    return feedback.reset_patterns()


@app.get("/documents")
def list_documents() -> dict:
    extracted_dir = Path("data/extracted")
    extracted_dir.mkdir(parents=True, exist_ok=True)
    docs = []
    for path in sorted(extracted_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        payload = json.loads(path.read_text(encoding="utf-8"))
        docs.append(
            {
                "doc_id": payload.get("doc_id"),
                "total_pages": payload.get("extraction_quality", {}).get("total_pages", 0),
                "pages_with_text": payload.get("extraction_quality", {}).get("pages_with_text", 0),
                "avg_confidence": payload.get("extraction_quality", {}).get("avg_confidence"),
                "warning_count": len(payload.get("extraction_warnings", [])),
            }
        )
    return {"count": len(docs), "documents": docs}


@app.get("/documents/{doc_id}")
def get_document(doc_id: str) -> dict:
    processed = _load_processed_doc(doc_id)
    return {
        "doc_id": doc_id,
        "extraction_quality": processed.get("extraction_quality", {}),
        "warnings": processed.get("extraction_warnings", []),
        "structured_fields": processed.get("structured_fields", {}),
    }


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str) -> dict:
    _load_processed_doc(doc_id)

    extracted_file = Path("data/extracted") / f"{doc_id}.json"
    upload_file = uploads_dir / f"{doc_id}.pdf"
    extracted_file.unlink(missing_ok=True)
    upload_file.unlink(missing_ok=True)

    deleted_chunks = embedder.delete_document_chunks(doc_id)
    return {
        "doc_id": doc_id,
        "status": "deleted",
        "deleted_chunks": deleted_chunks,
    }


@app.get("/review", response_class=HTMLResponse)
def review_ui() -> str:
    return """
    <html>
      <head><title>Operator Review</title></head>
      <body style="font-family: Arial, sans-serif; margin: 24px;">
        <h2>Operator Draft Review</h2>
        <p>Use this page to edit a generated draft and submit corrections.</p>
        <form id="review-form">
          <label>Doc ID</label><br />
          <input id="doc-id" style="width: 400px;" /><br /><br />
          <label>Original Draft</label><br />
          <textarea id="original" rows="10" cols="100"></textarea><br /><br />
          <label>Edited Draft</label><br />
          <textarea id="edited" rows="10" cols="100"></textarea><br /><br />
          <button type="submit">Save Edit</button>
        </form>
        <pre id="result"></pre>
        <script>
          document.getElementById("review-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const docId = document.getElementById("doc-id").value;
            const original = document.getElementById("original").value;
            const edited = document.getElementById("edited").value;
            const res = await fetch(`/edit/${docId}`, {
              method: "POST",
              headers: { "content-type": "application/json" },
              body: JSON.stringify({ original_draft: original, edited_draft: edited })
            });
            document.getElementById("result").textContent = JSON.stringify(await res.json(), null, 2);
          });
        </script>
      </body>
    </html>
    """
