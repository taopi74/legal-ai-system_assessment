from __future__ import annotations

from fastapi import APIRouter

from src.app_state import state
from src.schemas import RetrieveRequest

router = APIRouter()


@router.post("/retrieve/{doc_id}")
def retrieve(doc_id: str, payload: RetrieveRequest) -> dict:
    evidence = state.retriever.retrieve(doc_id=doc_id, query=payload.query, top_k=payload.top_k)
    return {"doc_id": doc_id, "query": payload.query, "evidence": evidence}


@router.post("/draft/{doc_id}")
def draft(doc_id: str, payload: RetrieveRequest) -> dict:
    processed = state.load_processed_doc(doc_id)
    evidence = state.retriever.retrieve(doc_id=doc_id, query=payload.query, top_k=payload.top_k)
    draft_payload = state.drafter.generate_grounded(processed.get("structured_fields", {}), evidence)
    return {
        "doc_id": doc_id,
        "draft": draft_payload["draft_text"],
        "citations": draft_payload["citations"],
        "evidence_count": draft_payload["evidence_count"],
        "evidence_map": state.retriever.build_evidence_map(evidence),
        "warning": "No evidence found for this query." if not evidence else None,
        "invalid_citations": draft_payload["invalid_citations"],
        "missing_section_citations": draft_payload["missing_section_citations"],
        "grounding_ok": draft_payload["grounding_ok"],
        "grounding_attempts": draft_payload["attempts"],
    }


@router.get("/draft/{doc_id}/evidence-map")
def draft_evidence_map(doc_id: str, query: str, top_k: int | None = None) -> dict:
    evidence = state.retriever.retrieve(doc_id=doc_id, query=query, top_k=top_k)
    return {"doc_id": doc_id, "query": query, "evidence_map": state.retriever.build_evidence_map(evidence)}
