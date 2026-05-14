import json

from fastapi.testclient import TestClient

from src import api
from src.config import AppPaths


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
    old_paths = api.state.paths
    api.state.paths = AppPaths(
        project_root=tmp_path,
        uploads_dir=tmp_path / "data" / "sample_inputs",
        extracted_dir=extracted_dir,
        web_dir=tmp_path / "web",
    )
    api.state.paths.uploads_dir.mkdir(parents=True, exist_ok=True)
    api.state.paths.web_dir.mkdir(parents=True, exist_ok=True)

    client = TestClient(api.app)
    listed = client.get("/documents")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1

    details = client.get("/documents/doc-1")
    assert details.status_code == 200
    assert details.json()["structured_fields"]["case_number"] == "ABC"
    api.state.paths = old_paths


def test_retrieve_validation_rejects_empty_query() -> None:
    client = TestClient(api.app)
    response = client.post("/retrieve/demo-doc", json={"query": ""})
    assert response.status_code == 422


def test_reset_patterns_endpoint() -> None:
    client = TestClient(api.app)
    response = client.post("/reset-patterns")
    assert response.status_code == 200
    assert response.json()["style_notes"] == []


def test_review_route_serves_static_html(tmp_path) -> None:
    web_dir = tmp_path / "web"
    web_dir.mkdir(parents=True, exist_ok=True)
    (web_dir / "review.html").write_text("<html><body>review-ui</body></html>", encoding="utf-8")

    old_paths = api.state.paths
    api.state.paths = AppPaths(
        project_root=tmp_path,
        uploads_dir=tmp_path / "data" / "sample_inputs",
        extracted_dir=tmp_path / "data" / "extracted",
        web_dir=web_dir,
    )
    api.state.paths.uploads_dir.mkdir(parents=True, exist_ok=True)
    api.state.paths.extracted_dir.mkdir(parents=True, exist_ok=True)

    client = TestClient(api.app)
    response = client.get("/review")
    assert response.status_code == 200
    assert "review-ui" in response.text
    api.state.paths = old_paths


def test_auth_middleware_rejects_invalid_api_key(monkeypatch) -> None:
    monkeypatch.setenv("BASIC_AUTH_API_KEY", "secret")
    client = TestClient(api.app)
    response = client.get("/health", headers={"x-api-key": "wrong"})
    assert response.status_code == 401
    monkeypatch.delenv("BASIC_AUTH_API_KEY")


def test_rate_limit_middleware_blocks_after_threshold(monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "1")
    api.state.reset_counters()
    client = TestClient(api.app)
    first = client.get("/health")
    second = client.get("/health")
    assert first.status_code == 200
    assert second.status_code == 429
    monkeypatch.delenv("RATE_LIMIT_PER_MINUTE")

