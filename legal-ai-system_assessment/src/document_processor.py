from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import pdfplumber
from pdf2image import convert_from_path

from src.llm_provider import GeminiProvider, get_provider
from src.prompt_loader import load_prompt


class DocumentProcessor:
    def __init__(self, data_dir: str = "data/extracted") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def process_pdf(self, file_path: str, doc_id: str) -> Dict[str, Any]:
        pages: List[Dict[str, Any]] = []
        all_text: List[str] = []
        warnings: List[str] = []
        ocr_provider: Any = GeminiProvider()
        fallback_indices: List[int] = []
        primary_text: Dict[int, str] = {}

        with pdfplumber.open(file_path) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                text = (page.extract_text() or "").strip()
                if len(text) < 40:
                    fallback_indices.append(idx)
                primary_text[idx] = text

        fallback_text = self.process_pages_parallel(file_path, fallback_indices, ocr_provider) if fallback_indices else {}
        total_pages = len(primary_text)
        for idx in range(1, total_pages + 1):
            text = primary_text.get(idx, "")
            method = "pdfplumber"
            confidence = 1.0 if text else 0.0
            if idx in fallback_indices:
                text = fallback_text.get(idx, "").strip()
                method = "gemini_vision_fallback"
                confidence = 0.75 if text else 0.2
                if not text:
                    warnings.append(f"Low OCR quality on page {idx}")
            page_payload = {
                "page_number": idx,
                "raw_text": text,
                "ocr_method": method,
                "confidence": round(confidence, 2),
            }
            pages.append(page_payload)
            if text:
                all_text.append(text)

        merged_text = "\n\n".join(all_text)
        structured = self.extract_structured_fields(merged_text)
        extraction_quality = {
            "total_pages": len(pages),
            "pages_with_text": sum(1 for p in pages if p["raw_text"]),
            "avg_confidence": round(
                sum(float(p["confidence"]) for p in pages) / max(len(pages), 1), 2
            ),
        }

        output = {
            "doc_id": doc_id,
            "pages": pages,
            "merged_text": merged_text,
            "structured_fields": structured,
            "extraction_quality": extraction_quality,
            "extraction_warnings": warnings,
        }
        (self.data_dir / f"{doc_id}.json").write_text(
            json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return output

    def extract_structured_fields(self, text: str) -> Dict[str, Any]:
        default = {
            "case_number": None,
            "parties": [],
            "key_dates": {},
            "jurisdiction": None,
            "document_type": None,
            "key_facts": [],
            "notable_gaps": [],
        }
        if not text.strip():
            return default
        template = load_prompt(
            "extraction_prompt.txt",
            (
                "Extract fields in JSON only with keys: case_number, parties, key_dates, "
                "jurisdiction, document_type, key_facts, notable_gaps. "
                "Do not hallucinate. Unknown -> null or empty array/object.\n\nText:\n{text}"
            ),
        )
        prompt = template.replace("{text}", text[:14000])
        provider = get_provider()
        parsed = provider.generate_json(prompt, fallback=default)
        for key, value in default.items():
            parsed.setdefault(key, value)
        return parsed

    def process_pages_parallel(self, file_path: str, page_numbers: List[int], provider: Any) -> Dict[int, str]:
        workers = int(os.getenv("OCR_MAX_WORKERS", "5"))
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {
                executor.submit(self._extract_page_text_with_vision, file_path, page_no, provider): page_no
                for page_no in page_numbers
            }
            return {futures[f]: f.result() for f in futures}

    def _extract_page_text_with_vision(self, file_path: str, page_number: int, provider: Any) -> str:
        vision_prompt = (
            "Perform OCR on this legal page. Return only extracted plain text. "
            "Preserve dates, names, amounts, headings, and list items."
        )
        try:
            images = convert_from_path(file_path, first_page=page_number, last_page=page_number, dpi=220)
            if not images:
                return ""
            return provider.ocr_from_image(images[0], vision_prompt).strip()
        except Exception:
            return ""
