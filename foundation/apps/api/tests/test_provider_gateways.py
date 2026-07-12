from __future__ import annotations

import json

import httpx

from app.core.config import Settings
from app.services.model_gateway import (
    CloudModelGateway,
    HermesModelGateway,
    RulesModelGateway,
    build_model_gateway,
)


def _transport(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    prompt = body["messages"][-1]["content"]
    if "Return a JSON object" in prompt:
        content = json.dumps(
            {
                "domain": "software",
                "intent": "build",
                "confidence": 0.91,
                "evidence": ["implementation queue"],
                "engine": "ignored-by-adapter",
                "needs_review": False,
            }
        )
    else:
        content = "A concise execution summary."
    return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})


async def test_cloud_gateway_returns_typed_outputs_and_uses_bearer_auth() -> None:
    seen_auth: list[str | None] = []

    def transport(request: httpx.Request) -> httpx.Response:
        seen_auth.append(request.headers.get("Authorization"))
        return _transport(request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as client:
        gateway = CloudModelGateway(
            base_url="https://models.example/v1",
            model="cloud-model",
            api_key="secret",
            client=client,
        )
        summary = await gateway.summarize("Build an implementation queue.")
        classification = await gateway.classify(
            "Queue", "Build an implementation queue.", "software"
        )

    assert summary == "A concise execution summary."
    assert classification.domain == "software"
    assert classification.engine == "cloud:cloud-model"
    assert seen_auth == ["Bearer secret", "Bearer secret"]


async def test_hermes_gateway_works_without_api_key() -> None:
    async with httpx.AsyncClient(transport=httpx.MockTransport(_transport)) as client:
        gateway = HermesModelGateway(
            base_url="http://hermes.local:8080/v1",
            model="hermes-3",
            client=client,
        )
        result = await gateway.classify("Queue", "Build an implementation queue.", None)

    assert result.engine == "hermes:hermes-3"


def test_gateway_factory_selects_configured_provider() -> None:
    rules = build_model_gateway(Settings(model_provider="rules"))
    hermes = build_model_gateway(
        Settings(
            model_provider="hermes",
            model_base_url="http://localhost:8080/v1",
            model_name="hermes-3",
        )
    )
    cloud = build_model_gateway(
        Settings(
            model_provider="cloud",
            model_base_url="https://models.example/v1",
            model_name="cloud-model",
            model_api_key="secret",
        )
    )

    assert isinstance(rules, RulesModelGateway)
    assert isinstance(hermes, HermesModelGateway)
    assert isinstance(cloud, CloudModelGateway)
