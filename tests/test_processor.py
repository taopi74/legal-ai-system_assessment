from src.document_processor import DocumentProcessor


def test_extract_structured_fields_empty_text() -> None:
    processor = DocumentProcessor()
    fields = processor.extract_structured_fields("")
    assert fields["case_number"] is None
    assert fields["parties"] == []


def test_parallel_method_returns_page_map(monkeypatch) -> None:
    processor = DocumentProcessor()

    def fake_extract(file_path, page_number, provider):  # noqa: ANN001
        return f"text-{page_number}"

    monkeypatch.setattr(processor, "_extract_page_text_with_vision", fake_extract)
    out = processor.process_pages_parallel("dummy.pdf", [1, 2], provider=object())
    assert out[1] == "text-1"
    assert out[2] == "text-2"
