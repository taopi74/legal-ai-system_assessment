from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from src.config import AppPaths, get_app_paths
from src.document_processor import DocumentProcessor
from src.draft_generator import DraftGenerator
from src.embedder import Embedder
from src.feedback_loop import FeedbackLoop
from src.retriever import Retriever


class AppState:
    def __init__(self, paths: AppPaths | None = None) -> None:
        self.paths = paths or get_app_paths()
        self.processor = DocumentProcessor()
        self.embedder = Embedder()
        self.retriever = Retriever()
        self.drafter = DraftGenerator()
        self.feedback = FeedbackLoop()
        self.request_counters: dict[str, dict[str, int]] = {}

    def reset_counters(self) -> None:
        self.request_counters.clear()

    def load_processed_doc(self, doc_id: str) -> dict:
        extracted_file = self.paths.extracted_dir / f"{doc_id}.json"
        if not extracted_file.exists():
            raise HTTPException(status_code=404, detail="Document not found.")
        return json.loads(extracted_file.read_text(encoding="utf-8"))

    async def save_upload(self, file: UploadFile) -> tuple[str, Path]:
        doc_id = str(uuid.uuid4())
        out_path = self.paths.uploads_dir / f"{doc_id}.pdf"
        out_path.write_bytes(await file.read())
        return doc_id, out_path


state = AppState()
