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
        payload = self.generate_grounded(structured_data, evidence)
        return payload["draft_text"]

    def generate_grounded(self, structured_data: Dict[str, Any], evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        provider = get_provider()
        patterns = self._load_patterns()
        evidence_text = "\n\n".join(
            (
                f"- evidence_id={e.get('evidence_id')}\n"
                f"  text={e['chunk_text']}\n"
                f"  source={e.get('metadata', {})}"
            )
            for e in evidence
        )
        prompt = (
            "You are a legal assistant. Write CASE FACT SUMMARY using only evidence.\n"
            "If unclear write: Unclear from documents.\n"
            "After each major claim add [evidence_id].\n\n"
            f"Learned preferences:\n{json.dumps(patterns, ensure_ascii=False)}\n\n"
            f"Structured fields:\n{json.dumps(structured_data, ensure_ascii=False)}\n\n"
            f"Evidence:\n{evidence_text}\n\n"
            "Format:\n"
            "1. Parties Involved\n2. Key Dates\n3. Core Facts\n"
            "4. Document Type and Context\n5. Notable Gaps"
        )
        draft_text = provider.generate(prompt)
        citations = [e.get("evidence_id") for e in evidence if e.get("evidence_id")]
        return {
            "draft_text": draft_text,
            "citations": citations,
            "evidence_count": len(evidence),
        }
