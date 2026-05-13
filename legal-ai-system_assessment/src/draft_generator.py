from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.llm_provider import get_provider


class DraftGenerator:
    def __init__(self, pattern_file: str = "data/learned_patterns.json") -> None:
        self.pattern_file = Path(pattern_file)

    def _load_patterns(self) -> Dict[str, List[str]]:
        if not self.pattern_file.exists():
            return {"style_notes": [], "content_corrections": [], "structural_preferences": []}
        return json.loads(self.pattern_file.read_text(encoding="utf-8"))

    def generate(self, structured_data: Dict[str, Any], evidence: List[Dict[str, Any]]) -> str:
        provider = get_provider()
        patterns = self._load_patterns()
        evidence_text = "\n\n".join(
            f"- {e['chunk_text']}\n  source={e.get('metadata', {})}" for e in evidence
        )
        prompt = (
            "You are a legal assistant. Write CASE FACT SUMMARY using only evidence.\n"
            "If unclear write: Unclear from documents.\n\n"
            f"Learned preferences:\n{json.dumps(patterns, ensure_ascii=False)}\n\n"
            f"Structured fields:\n{json.dumps(structured_data, ensure_ascii=False)}\n\n"
            f"Evidence:\n{evidence_text}\n\n"
            "Format:\n"
            "1. Parties Involved\n2. Key Dates\n3. Core Facts\n"
            "4. Document Type and Context\n5. Notable Gaps"
        )
        return provider.generate(prompt)
