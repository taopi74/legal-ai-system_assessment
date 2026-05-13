from src.feedback_loop import FeedbackLoop


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


def test_reset_patterns(tmp_path) -> None:
    patterns = tmp_path / "learned_patterns.json"
    edits_dir = tmp_path / "edits"
    loop = FeedbackLoop(edits_dir=str(edits_dir), patterns_file=str(patterns))
    loop.save_edit("doc1", "A long section", "Short [doc1:chunk:0]")
    reset = loop.reset_patterns()
    assert reset["style_notes"] == []
