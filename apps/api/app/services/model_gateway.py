from __future__ import annotations

import json
import re
from typing import Any, Protocol

import httpx

from app.core.config import Settings
from app.schemas.classification import ClassificationResult
from app.services.classifier import classify_capture, summarize_capture


class ModelGateway(Protocol):
    async def summarize(self, content: str) -> str: ...

    async def classify(
        self, title: str, content: str, domain_hint: str | None
    ) -> ClassificationResult: ...


class RulesModelGateway:
    """Deterministic local gateway used when no configured model is required."""

    async def summarize(self, content: str) -> str:
        return summarize_capture(content)

    async def classify(
        self, title: str, content: str, domain_hint: str | None
    ) -> ClassificationResult:
        return ClassificationResult.model_validate(
            classify_capture(title, content, domain_hint)
        )


class ModelGatewayError(RuntimeError):
    pass


class _OpenAICompatibleModelGateway:
    provider_name = "compatible"

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str | None = None,
        timeout_seconds: float = 60.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.client = client

    async def _complete(self, system: str, prompt: str, *, temperature: float = 0.0) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload: dict[str, Any] = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        if self.client is not None:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )
        else:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=payload
                )
        try:
            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ModelGatewayError(f"Invalid model response: {exc}") from exc
        if not isinstance(content, str) or not content.strip():
            raise ModelGatewayError("Model returned empty content")
        return content.strip()

    async def summarize(self, content: str) -> str:
        return await self._complete(
            "You create faithful, concise summaries without inventing facts.",
            f"Summarize this captured context in no more than 180 words:\n\n{content}",
        )

    async def classify(
        self, title: str, content: str, domain_hint: str | None
    ) -> ClassificationResult:
        schema = ClassificationResult.model_json_schema()
        prompt = (
            "Return a JSON object only. Classify the capture using this JSON Schema: "
            f"{json.dumps(schema, separators=(',', ':'))}\n\n"
            f"Title: {title}\nDomain hint: {domain_hint or 'none'}\nContent:\n{content}"
        )
        raw = await self._complete(
            "You are the intake classifier for Ryan Agent OS. Evidence must quote short phrases "
            "from the supplied capture.",
            prompt,
        )
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.IGNORECASE)
        try:
            result = ClassificationResult.model_validate_json(cleaned)
        except ValueError as exc:
            raise ModelGatewayError(f"Classification did not match schema: {exc}") from exc
        return result.model_copy(update={"engine": f"{self.provider_name}:{self.model}"})


class CloudModelGateway(_OpenAICompatibleModelGateway):
    provider_name = "cloud"


class HermesModelGateway(_OpenAICompatibleModelGateway):
    provider_name = "hermes"


def build_model_gateway(settings: Settings) -> ModelGateway:
    if settings.model_provider == "rules":
        return RulesModelGateway()
    if settings.model_provider == "hermes":
        return HermesModelGateway(
            base_url=settings.model_base_url,
            model=settings.model_name,
            api_key=settings.model_api_key or None,
            timeout_seconds=settings.model_timeout_seconds,
        )
    if settings.model_provider == "cloud":
        return CloudModelGateway(
            base_url=settings.model_base_url,
            model=settings.model_name,
            api_key=settings.model_api_key or None,
            timeout_seconds=settings.model_timeout_seconds,
        )
    raise ValueError(f"Unsupported model provider: {settings.model_provider}")
