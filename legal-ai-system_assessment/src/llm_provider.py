import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Protocol

import google.generativeai as genai
from dotenv import load_dotenv
try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover
    Anthropic = None

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

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
        self._max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        self._timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
        self._backoff_seconds = float(os.getenv("LLM_BACKOFF_SECONDS", "1.0"))

    def _with_retry(self, fn):
        for attempt in range(self._max_retries):
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(fn)
                    return future.result(timeout=self._timeout_seconds)
            except Exception:
                if attempt == self._max_retries - 1:
                    raise
                sleep_time = self._backoff_seconds * (2**attempt) + random.uniform(0, 0.2)
                time.sleep(sleep_time)

    def generate(self, prompt: str) -> str:
        response = self._with_retry(lambda: self._model.generate_content(prompt, stream=False))
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
        response = self._with_retry(lambda: self._model.generate_content([prompt, image], stream=False))
        return (getattr(response, "text", "") or "").strip()


class ClaudeProvider:
    def __init__(self) -> None:
        if Anthropic is None:
            raise RuntimeError("anthropic package is not installed.")
        self._client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        self._model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")

    def generate(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        if not message.content:
            return ""
        return getattr(message.content[0], "text", "").strip()

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
        raise NotImplementedError("Claude provider does not support OCR in this project.")


class OpenAIProvider:
    def __init__(self) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package is not installed.")
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str) -> str:
        response = self._client.responses.create(model=self._model, input=prompt)
        return (getattr(response, "output_text", "") or "").strip()

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
        raise NotImplementedError("OpenAI provider does not support OCR in this project.")


def get_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider == "gemini":
        return GeminiProvider()
    if provider == "claude":
        return ClaudeProvider()
    if provider == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unsupported provider: {provider}")
