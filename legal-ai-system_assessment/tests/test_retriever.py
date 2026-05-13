from src.retriever import Retriever


def test_retriever_evidence_map_shape() -> None:
    retriever = Retriever()
    evidence = [
        {
            "evidence_id": "a:chunk:1",
            "metadata": {"chunk_index": 1, "page_hint": "1", "page_number": 1},
            "score": 0.7,
        }
    ]
    mapped = retriever.build_evidence_map(evidence)
    assert mapped[0]["evidence_id"] == "a:chunk:1"
    assert mapped[0]["page_number"] == 1


def test_retriever_empty_query_returns_empty() -> None:
    retriever = Retriever()
    assert retriever.retrieve(doc_id="doc-x", query="   ", top_k=3) == []
