from __future__ import annotations

from pydantic import BaseModel, Field


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
