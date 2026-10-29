"""The AI boundary.

Two rules:
  1. Nothing above this file knows which provider is active.
  2. `complete_json` validates against a Pydantic schema and retries once
     on failure, then raises `LLMContractError`. Callers never see raw JSON.

Groq and Together both speak the OpenAI wire format, so there is exactly
one client class: `OpenAICompatClient`.
"""

from __future__ import annotations

import json
from typing import Protocol, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from postwise.config import Settings

T = TypeVar("T", bound=BaseModel)


class LLMContractError(RuntimeError):
    """Raised when the model returns something that does not match the schema."""

    def __init__(self, schema: type[BaseModel], raw: str) -> None:
        super().__init__(f"model output did not match {schema.__name__}: {raw[:500]!r}")
        self.schema = schema
        self.raw = raw


class LLMClient(Protocol):
    def complete(self, *, system: str, user: str) -> str: ...
    def complete_json(self, *, system: str, user: str, schema: type[T]) -> T: ...


# ---------------------------------------------------------------------------
# Real client — works for Groq AND Together. Only base_url + key differ.
# ---------------------------------------------------------------------------
_BASE_URLS: dict[str, str] = {
    "groq": "https://api.groq.com/openai/v1",
    "together": "https://api.together.xyz/v1",
}


class OpenAICompatClient:
    """One class, two providers. The base URL decides which one."""

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        api_key: str,
        timeout_s: int = 30,
        max_retries: int = 2,
    ) -> None:
        if provider not in _BASE_URLS:
            raise ValueError(f"unknown provider: {provider!r}")
        self._provider = provider
        self._model = model
        self._client = OpenAI(
            base_url=_BASE_URLS[provider],
            api_key=api_key,
            timeout=timeout_s,
            max_retries=max_retries,
        )

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    def complete(self, *, system: str, user: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
        )
        content = response.choices[0].message.content
        if not content:
            raise LLMContractError(schema=BaseModel, raw="")
        return content

    def complete_json(self, *, system: str, user: str, schema: type[T]) -> T:
        """Ask for JSON, validate it, retry once, then raise."""
        last_raw = ""
        for attempt in range(2):
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            last_raw = response.choices[0].message.content or ""
            try:
                payload = json.loads(last_raw)
                return schema.model_validate(payload)
            except (json.JSONDecodeError, ValidationError):
                if attempt == 0:
                    continue
        raise LLMContractError(schema=schema, raw=last_raw)


# ---------------------------------------------------------------------------
# Factory — the only place in the codebase that reads provider settings.
# ---------------------------------------------------------------------------
def get_client(settings: Settings) -> LLMClient:
    """Return the primary client. Fake only when provider is 'fake'."""
    if settings.llm_provider == "fake":
        from postwise.ai.fake import FakeLLM

        return FakeLLM()

    if settings.llm_api_key is None:
        raise ValueError(f"POSTWISE_LLM_API_KEY is required for provider={settings.llm_provider!r}")

    return OpenAICompatClient(
        provider=settings.llm_provider,
        model=settings.llm_model,
        api_key=settings.llm_api_key.get_secret_value(),
        timeout_s=settings.llm_timeout_s,
        max_retries=settings.llm_max_retries,
    )
