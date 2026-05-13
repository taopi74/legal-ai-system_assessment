from src.embedder import Embedder
from src.feedback_loop import FeedbackLoop
from src.retriever import Retriever


def test_chunking_works() -> None:
    text = "A" * 3000
    chunks = Embedder.chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) >= 3
    assert chunks[0]


def test_feedback_loop_patterns(tmp_path) -> None:
    patterns = tmp_path / "learned_patterns.json"
    edits_dir = tmp_path / "edits"
    loop = FeedbackLoop(edits_dir=str(edits_dir), patterns_file=str(patterns))
    loop.save_edit(
        "doc1",
        "This is a long draft without evidence tags and with redundant details.",
        "Short [doc1:chunk:0]\nNotable gaps\nUnclear from documents",
    )
    data = loop.get_patterns()
    assert data["style_notes"]
    assert data["structural_preferences"]


def test_retriever_evidence_map_shape() -> None:
    retriever = Retriever()
    evidence = [{"evidence_id": "a:chunk:1", "metadata": {"chunk_index": 1, "page_hint": "1,2"}, "score": 0.7}]
    mapped = retriever.build_evidence_map(evidence)
    assert mapped[0]["evidence_id"] == "a:chunk:1"
