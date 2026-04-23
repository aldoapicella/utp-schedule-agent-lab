from __future__ import annotations

import json
import os
from typing import Any

import httpx

from schedule_agent.llm.base import GeneratedResponse, LLMClient, LLMProviderError


class OpenAILLM(LLMClient):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMProviderError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.timeout_seconds = timeout_seconds

    def compose_response(self, context: dict[str, Any]) -> GeneratedResponse:
        prompt = self._build_prompt(context)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente académico cuidadoso para planificación de horarios. "
                        "Responde siempre en español. "
                        "Devuelve JSON compacto con las llaves assistant_message y explanation. "
                        "explanation debe ser un arreglo de frases breves en español. "
                        "No sugieras matrícula, inscripción ni ninguna acción oficial. "
                        "Este laboratorio solo recomienda horarios."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "schedule_agent_response",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "assistant_message": {"type": "string"},
                            "explanation": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["assistant_message", "explanation"],
                    },
                },
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            if response.status_code >= 400:
                raise LLMProviderError(
                    f"OpenAI request failed with status {response.status_code}: {response.text[:200]}"
                )
            body = response.json()

        try:
            content = body["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMProviderError("OpenAI response did not match the expected JSON contract.") from exc

        explanation = parsed.get("explanation") or []
        if not isinstance(explanation, list):
            explanation = [str(explanation)]
        return GeneratedResponse(
            assistant_message=str(parsed.get("assistant_message", "")).strip()
            or "OpenAI generated a response.",
            explanation=[str(item) for item in explanation],
        )

    @staticmethod
    def _build_prompt(context: dict[str, Any]) -> str:
        return json.dumps(
            {
                "recommended_schedule": context.get("recommended_schedule") or [],
                "requested_subject_count": context.get("requested_subject_count") or 0,
                "explanation_lines": context.get("explanation_lines") or [],
                "human_review": context.get("human_review"),
            },
            ensure_ascii=False,
        )
