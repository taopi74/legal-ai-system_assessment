from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from src.llm_provider import get_provider
from src.prompt_loader import load_prompt


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
        template = load_prompt(
            "generation_prompt.txt",
            (
                "You are a legal assistant. Write CASE FACT SUMMARY using only evidence.\n"
                "If unclear write: Unclear from documents.\n"
                "After each major claim add [evidence_id].\n\n"
                "Learned preferences:\n{learned_patterns}\n\n"
                "Evidence:\n{evidence}\n\n"
                "Structured fields:\n{structured_data}\n\n"
                "Format:\n1. Parties Involved\n2. Key Dates\n3. Core Facts\n"
                "4. Document Type and Context\n5. Notable Gaps"
            ),
        )
        prompt = (
            template.replace("{learned_patterns}", json.dumps(patterns, ensure_ascii=False))
            .replace("{evidence}", evidence_text)
            .replace("{retrieved_chunks}", evidence_text)
            .replace("{structured_data}", json.dumps(structured_data, ensure_ascii=False))
            .replace("{structured_fields}", json.dumps(structured_data, ensure_ascii=False))
        )
        draft_text = provider.generate(prompt)
        max_attempts = self._env_int("GROUNDING_MAX_ATTEMPTS", 2)
        citations = [e.get("evidence_id") for e in evidence if e.get("evidence_id")]
        invalid_citations = self._invalid_citations(draft_text, citations)
        missing_section_citations = self._sections_missing_citation(draft_text)
        auto_regen = self._env_bool("GROUNDING_AUTO_REGENERATE", True)
        attempts = 1
        while auto_regen and attempts < max_attempts and (invalid_citations or missing_section_citations):
            correction = (
                "\n\nYour previous output violated grounding checks.\n"
                f"Invalid citation ids: {invalid_citations}\n"
                f"Sections missing citations: {missing_section_citations}\n"
                "Regenerate the full draft with valid evidence ids and at least one citation in each numbered section."
            )
            draft_text = provider.generate(prompt + correction)
            invalid_citations = self._invalid_citations(draft_text, citations)
            missing_section_citations = self._sections_missing_citation(draft_text)
            attempts += 1
        return {
            "draft_text": draft_text,
            "citations": citations,
            "evidence_count": len(evidence),
            "invalid_citations": invalid_citations,
            "missing_section_citations": missing_section_citations,
            "grounding_ok": len(invalid_citations) == 0 and len(missing_section_citations) == 0,
            "attempts": attempts,
        }

    @staticmethod
    def _invalid_citations(draft_text: str, valid_citations: List[str]) -> List[str]:
        cited_tags = set(re.findall(r"\[([^\[\]]+)\]", draft_text))
        return sorted(tag for tag in cited_tags if tag not in valid_citations)

    @staticmethod
    def _sections_missing_citation(draft_text: str) -> List[str]:
        heading_pattern = re.compile(r"^\s*(?:#+\s*)?(\d+)\.\s+(.+)$", re.MULTILINE)
        matches = list(heading_pattern.finditer(draft_text))
        missing: List[str] = []
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(draft_text)
            section_body = draft_text[start:end]
            if not re.search(r"\[[^\[\]]+\]", section_body):
                title = f"{match.group(1)}. {match.group(2).strip()}"
                missing.append(title)
        return missing

    @staticmethod
    def _env_bool(key: str, default: bool) -> bool:
        raw = os.getenv(key)
        if raw is None:
            return default
        return raw.lower() in {"1", "true", "yes"}

    @staticmethod
    def _env_int(key: str, default: int) -> int:
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            return max(1, int(raw))
        except ValueError:
            return default
