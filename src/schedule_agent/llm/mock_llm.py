from __future__ import annotations

from schedule_agent.llm.base import GeneratedResponse, LLMClient


class MockLLM(LLMClient):
    def compose_response(self, context: dict) -> GeneratedResponse:
        if context.get("human_review"):
            reason = context["human_review"]["reason"]
            assistant_message = (
                "Necesito escalar este caso a un asesor humano antes de recomendar un horario definitivo."
            )
            explanation = [
                f"Motivo de escalamiento: {reason}.",
                "El agente no debe ignorar reglas académicas ni completar acciones no seguras.",
            ]
            return GeneratedResponse(assistant_message=assistant_message, explanation=explanation)

        recommended = context.get("recommended_schedule") or []
        if not recommended:
            return GeneratedResponse(
                assistant_message="No encontré un horario válido con las restricciones actuales.",
                explanation=context.get("explanation_lines") or ["No hubo combinaciones factibles."],
            )

        lines = [
            "Recomendé la combinación con mayor cobertura válida y menor tiempo muerto.",
            *(context.get("explanation_lines") or []),
        ]
        assistant_message = "Encontré un horario factible y ya validé las restricciones principales."
        return GeneratedResponse(assistant_message=assistant_message, explanation=lines)

