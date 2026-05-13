from __future__ import annotations

import difflib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from src.llm_provider import get_provider
from src.prompt_loader import load_prompt


class FeedbackLoop:
    def __init__(
        self,
        edits_dir: str = "data/edits",
        patterns_file: str = "data/learned_patterns.json",
        sqlite_file: str = "data/edits.db",
        storage_backend: str | None = None,
    ) -> None:
        self.edits_dir = Path(edits_dir)
        self.patterns_file = Path(patterns_file)
        self.sqlite_file = Path(sqlite_file)
        self.storage_backend = (storage_backend or os.getenv("STORAGE_BACKEND", "json")).lower()
        self.edits_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.patterns_file.exists():
            self.patterns_file.write_text(
                json.dumps(
                    {"style_notes": [], "content_corrections": [], "structural_preferences": []},
                    indent=2,
                ),
                encoding="utf-8",
            )
        if self.storage_backend in {"sqlite", "hybrid"}:
            self._init_sqlite()

    def _init_sqlite(self) -> None:
        with sqlite3.connect(self.sqlite_file) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS edits (
                    edit_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    edited_text TEXT NOT NULL,
                    diff_summary TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_edit(self, doc_id: str, original_text: str, edited_text: str) -> Dict[str, str]:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        edit_id = f"{doc_id}_{timestamp}"
        diff = "\n".join(
            difflib.unified_diff(
                original_text.splitlines(),
                edited_text.splitlines(),
                fromfile="original",
                tofile="edited",
                lineterm="",
            )
        )
        payload = {
            "edit_id": edit_id,
            "doc_id": doc_id,
            "original_text": original_text,
            "edited_text": edited_text,
            "diff_summary": diff,
        }
        if self.storage_backend in {"json", "hybrid"}:
            (self.edits_dir / f"{edit_id}.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        if self.storage_backend in {"sqlite", "hybrid"}:
            with sqlite3.connect(self.sqlite_file) as conn:
                conn.execute(
                    """
                    INSERT INTO edits (edit_id, doc_id, timestamp, original_text, edited_text, diff_summary)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (edit_id, doc_id, timestamp, original_text, edited_text, diff),
                )
                conn.commit()
        learned = self._update_patterns_with_llm(original_text, edited_text)
        return {"edit_id": edit_id, "status": "saved", "patterns_added": str(learned)}

    def _update_patterns_with_llm(self, original_text: str, edited_text: str) -> int:
        default = {"style_notes": [], "content_corrections": [], "structural_preferences": []}
        template = load_prompt(
            "feedback_prompt.txt",
            (
                "An operator edited an AI-generated legal draft.\n\n"
                "Original: {original}\nEdited: {edited}\n\n"
                "Analyze what changed and return JSON with keys: "
                "style_notes, content_corrections, structural_preferences."
            ),
        )
        prompt = template.replace("{original}", original_text[:6000]).replace("{edited}", edited_text[:6000])
        try:
            learned = get_provider().generate_json(prompt, fallback=default)
        except Exception:
            learned = default
        return self._merge_patterns(learned, original_text, edited_text)

    def _merge_patterns(self, learned: Dict[str, List[str]], original_text: str, edited_text: str) -> int:
        data = json.loads(self.patterns_file.read_text(encoding="utf-8"))
        added = 0
        for key in ("style_notes", "content_corrections", "structural_preferences"):
            for note in learned.get(key, []) or []:
                if isinstance(note, str) and note.strip() and note not in data[key]:
                    data[key].append(note.strip())
                    added += 1
        if len(edited_text) < len(original_text):
            note = "Prefer concise sections and remove redundant details."
            if note not in data["style_notes"]:
                data["style_notes"].append(note)
                added += 1
        if "[" in edited_text and "]" in edited_text:
            note = "Include explicit evidence tags after key claims."
            if note not in data["structural_preferences"]:
                data["structural_preferences"].append(note)
                added += 1
        if "Unclear from documents" in edited_text:
            note = "Explicitly mark unknown facts as unclear from documents."
            if note not in data["content_corrections"]:
                data["content_corrections"].append(note)
                added += 1
        if "notable gaps" in edited_text.lower():
            note = "Always include a dedicated Notable Gaps section."
            if note not in data["structural_preferences"]:
                data["structural_preferences"].append(note)
                added += 1
        self.patterns_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return added

    def get_patterns(self) -> Dict[str, List[str]]:
        return json.loads(self.patterns_file.read_text(encoding="utf-8"))

    def reset_patterns(self) -> Dict[str, List[str]]:
        reset_data = {"style_notes": [], "content_corrections": [], "structural_preferences": []}
        self.patterns_file.write_text(json.dumps(reset_data, indent=2), encoding="utf-8")
        return reset_data
