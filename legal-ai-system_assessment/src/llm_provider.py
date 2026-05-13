import os
from typing import Protocol

import google.generativeai as genai


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str:
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


def get_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unsupported provider: {provider}")
