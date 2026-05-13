from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pdfplumber

from src.llm_provider import get_provider


class DocumentProcessor:
    def __init__(self, data_dir: str = "data/extracted") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def process_pdf(self, file_path: str, doc_id: str) -> Dict[str, Any]:
        pages: List[Dict[str, Any]] = []
        all_text: List[str] = []

        with pdfplumber.open(file_path) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                text = (page.extract_text() or "").strip()
                pages.append(
                    {
                        "page_number": idx,
                        "raw_text": text,
                        "ocr_method": "pdfplumber",
                        "confidence": 1.0 if text else 0.0,
                    }
                )
                if text:
                    all_text.append(text)

        merged_text = "\n\n".join(all_text)
        structured = self.extract_structured_fields(merged_text)

        output = {
            "doc_id": doc_id,
            "pages": pages,
            "merged_text": merged_text,
            "structured_fields": structured,
        }
        (self.data_dir / f"{doc_id}.json").write_text(
            json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return output

    def extract_structured_fields(self, text: str) -> Dict[str, Any]:
        prompt = (
            "Extract fields in JSON: case_number, parties, key_dates, jurisdiction, "
            "document_type, key_facts, notable_gaps. If unknown return null.\n\n"
            f"Text:\n{text[:12000]}"
        )
        provider = get_provider()
        raw = provider.generate(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            return json.loads(raw[start : end + 1]) if start != -1 and end != -1 else {}
        except Exception:
            return {}
