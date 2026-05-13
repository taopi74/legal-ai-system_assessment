from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.document_processor import DocumentProcessor
from src.draft_generator import DraftGenerator
from src.embedder import Embedder
from src.feedback_loop import FeedbackLoop
from src.retriever import Retriever

app = FastAPI(title="Legal AI System")

uploads_dir = Path("data/sample_inputs")
uploads_dir.mkdir(parents=True, exist_ok=True)

processor = DocumentProcessor()
embedder = Embedder()
retriever = Retriever()
drafter = DraftGenerator()
feedback = FeedbackLoop()


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)


class EditRequest(BaseModel):
    original_draft: str
    edited_draft: str


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
