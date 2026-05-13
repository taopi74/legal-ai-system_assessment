import json
from pathlib import Path

from fastapi.testclient import TestClient

from src import api


def test_documents_list_and_details(tmp_path, monkeypatch) -> None:
    extracted_dir = tmp_path / "data" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "doc_id": "doc-1",
        "extraction_quality": {"total_pages": 2, "pages_with_text": 2, "avg_confidence": 0.9},
        "extraction_warnings": [],
        "structured_fields": {"case_number": "ABC"},
    }
    (extracted_dir / "doc-1.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    client = TestClient(api.app)
    listed = client.get("/documents")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1

    details = client.get("/documents/doc-1")
    assert details.status_code == 200
    assert details.json()["structured_fields"]["case_number"] == "ABC"


def test_retrieve_validation_rejects_empty_query() -> None:
    client = TestClient(api.app)
    response = client.post("/retrieve/demo-doc", json={"query": ""})
    assert response.status_code == 422


def test_reset_patterns_endpoint() -> None:
    client = TestClient(api.app)
    response = client.post("/reset-patterns")
    assert response.status_code == 200
    assert response.json()["style_notes"] == []

