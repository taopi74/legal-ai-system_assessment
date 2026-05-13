from __future__ import annotations

from fastapi import APIRouter

from src.app_state import state
from src.schemas import EditRequest, ResetPatternsResponse

router = APIRouter()


@router.post("/edit/{doc_id}")
def edit(doc_id: str, payload: EditRequest) -> dict:
    result = state.feedback.save_edit(
        doc_id=doc_id,
        original_text=payload.original_draft,
        edited_text=payload.edited_draft,
    )
    return {"doc_id": doc_id, **result, "patterns": state.feedback.get_patterns()}


@router.get("/patterns")
def patterns() -> dict:
    return state.feedback.get_patterns()


@router.post("/reset-patterns", response_model=ResetPatternsResponse)
def reset_patterns() -> dict:
    return state.feedback.reset_patterns()
