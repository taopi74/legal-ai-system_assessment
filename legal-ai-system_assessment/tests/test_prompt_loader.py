from src.prompt_loader import load_prompt


def test_prompt_loader_fallback_when_file_missing() -> None:
    fallback = "fallback-prompt"
    loaded = load_prompt("missing_prompt_file.txt", fallback)
    assert loaded == fallback
