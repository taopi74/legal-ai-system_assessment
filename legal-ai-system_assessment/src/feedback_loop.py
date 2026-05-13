from __future__ import annotations

import difflib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class FeedbackLoop:
    def __init__(
        self,
        edits_dir: str = "data/edits",
        patterns_file: str = "data/learned_patterns.json",
    ) -> None:
        self.edits_dir = Path(edits_dir)
        self.patterns_file = Path(patterns_file)
        self.edits_dir.mkdir(parents=True, exist_ok=True)
        if not self.patterns_file.exists():
            self.patterns_file.write_text(
                json.dumps(
                    {"style_notes": [], "content_corrections": [], "structural_preferences": []},
                    indent=2,
                ),
                encoding="utf-8",
            )

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
        (self.edits_dir / f"{edit_id}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        learned = self._update_patterns(original_text, edited_text)
        return {"edit_id": edit_id, "status": "saved", "patterns_added": str(learned)}

    def _update_patterns(self, original_text: str, edited_text: str) -> int:
        data = json.loads(self.patterns_file.read_text(encoding="utf-8"))
        added = 0
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
