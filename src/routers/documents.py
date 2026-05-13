from __future__ import annotations

import json

from fastapi import APIRouter

from src.app_state import state

router = APIRouter()


@router.get("/documents")
def list_documents() -> dict:
    docs = []
    for path in sorted(state.paths.extracted_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
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


@router.get("/documents/{doc_id}")
def get_document(doc_id: str) -> dict:
    processed = state.load_processed_doc(doc_id)
    return {
        "doc_id": doc_id,
        "extraction_quality": processed.get("extraction_quality", {}),
        "warnings": processed.get("extraction_warnings", []),
        "structured_fields": processed.get("structured_fields", {}),
    }


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str) -> dict:
    state.load_processed_doc(doc_id)
    extracted_file = state.paths.extracted_dir / f"{doc_id}.json"
    upload_file = state.paths.uploads_dir / f"{doc_id}.pdf"
    extracted_file.unlink(missing_ok=True)
    upload_file.unlink(missing_ok=True)
    deleted_chunks = state.embedder.delete_document_chunks(doc_id)
    return {
        "doc_id": doc_id,
        "status": "deleted",
        "deleted_chunks": deleted_chunks,
    }
