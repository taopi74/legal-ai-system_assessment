import json
import os
from typing import Any, Protocol

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str:
        ...

    def generate_json(self, prompt: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
        ...

    def ocr_from_image(self, image: Any, prompt: str) -> str:
        ...


class GeminiProvider:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        model = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:
        response = self._model.generate_content(prompt, stream=False)
        return (getattr(response, "text", "") or "").strip()

    def generate_json(self, prompt: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
        raw = self.generate(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(raw[start : end + 1])
        except Exception:
            pass
        return fallback or {}

    def ocr_from_image(self, image: Any, prompt: str) -> str:
        response = self._model.generate_content([prompt, image], stream=False)
        return (getattr(response, "text", "") or "").strip()


def get_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unsupported provider: {provider}")
