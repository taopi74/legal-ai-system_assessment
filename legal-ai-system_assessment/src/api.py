from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

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
    query: str
    top_k: int | None = None


class EditRequest(BaseModel):
    original_draft: str
    edited_draft: str


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
    embed_stats = embedder.index_document(doc_id, processed.get("merged_text", ""))
    return {"doc_id": doc_id, "embed": embed_stats, "status": "processed"}


@app.post("/retrieve/{doc_id}")
def retrieve(doc_id: str, payload: RetrieveRequest) -> dict:
    evidence = retriever.retrieve(doc_id=doc_id, query=payload.query, top_k=payload.top_k)
    return {"doc_id": doc_id, "query": payload.query, "evidence": evidence}


@app.post("/draft/{doc_id}")
def draft(doc_id: str, payload: RetrieveRequest) -> dict:
    extracted_file = Path("data/extracted") / f"{doc_id}.json"
    if not extracted_file.exists():
        raise HTTPException(status_code=404, detail="Document not found.")
    processed = json.loads(extracted_file.read_text(encoding="utf-8"))
    evidence = retriever.retrieve(doc_id=doc_id, query=payload.query, top_k=payload.top_k)
    draft_text = drafter.generate(processed.get("structured_fields", {}), evidence)
    return {"doc_id": doc_id, "draft": draft_text, "evidence_count": len(evidence)}


@app.post("/edit/{doc_id}")
def edit(doc_id: str, payload: EditRequest) -> dict:
    result = feedback.save_edit(
        doc_id=doc_id,
        original_text=payload.original_draft,
        edited_text=payload.edited_draft,
    )
    return {"doc_id": doc_id, **result}


@app.get("/patterns")
def patterns() -> dict:
    return feedback.get_patterns()
