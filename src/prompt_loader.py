from __future__ import annotations

from pathlib import Path


PROMPT_DIR = Path("prompts")


def load_prompt(file_name: str, default_text: str) -> str:
    path = PROMPT_DIR / file_name
    if not path.exists():
        return default_text
    return path.read_text(encoding="utf-8")
