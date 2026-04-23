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
            explanation = context.get("explanation_lines") or ["No hubo combinaciones factibles."]
            return GeneratedResponse(
                assistant_message=(
                    "No encontre un horario valido con esas restricciones, "
                    "pero te deje sugerencias para ajustarlo."
                ),
                explanation=explanation,
            )

        requested_subject_count = int(context.get("requested_subject_count") or len(recommended))
        subject_names = [str(item.get("subject_name", "")).strip() for item in recommended]
        subject_summary = ", ".join(name for name in subject_names if name) or "las materias solicitadas"
        if len(recommended) < requested_subject_count:
            lines = context.get("explanation_lines") or []
            assistant_message = (
                f"Encontre una alternativa parcial para {subject_summary}; "
                "algunas materias quedaron fuera por tus restricciones."
            )
            return GeneratedResponse(assistant_message=assistant_message, explanation=lines)

        lines = [
            "Recomendé la combinación con mayor cobertura válida y menor tiempo muerto.",
            *(context.get("explanation_lines") or []),
        ]
        assistant_message = (
            f"Encontré un horario factible para {subject_summary} y ya validé las restricciones principales."
        )
        return GeneratedResponse(assistant_message=assistant_message, explanation=lines)
