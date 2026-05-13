from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.app_state import state

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF is supported.")
    doc_id, out_path = await state.save_upload(file)
    processed = state.processor.process_pdf(str(out_path), doc_id)
    embed_stats = state.embedder.index_document(
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


@router.get("/review")
def review_ui() -> FileResponse:
    return FileResponse(state.paths.web_dir / "review.html")
