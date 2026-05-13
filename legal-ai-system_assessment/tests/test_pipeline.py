from src.embedder import Embedder


def test_chunking_works() -> None:
    text = "A" * 3000
    chunks = Embedder.chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) >= 3
    assert chunks[0]
