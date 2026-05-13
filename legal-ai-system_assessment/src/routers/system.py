from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.app_state import state

router = APIRouter()


@router.get("/health")
def health() -> dict:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    llm_configured = False
    if provider == "gemini":
        llm_configured = bool(os.getenv("GEMINI_API_KEY"))
    elif provider == "claude":
        llm_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    elif provider == "openai":
        llm_configured = bool(os.getenv("OPENAI_API_KEY"))
    chroma_dir = Path(os.getenv("CHROMA_DIR", "./data/chroma"))
    return {
        "status": "ok",
        "dependencies": {
            "provider": provider,
            "llm_configured": llm_configured,
            "chroma_dir_exists": chroma_dir.exists(),
        },
    }


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
