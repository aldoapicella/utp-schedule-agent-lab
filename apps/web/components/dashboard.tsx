"use client";

import { useEffect, useMemo, useState } from "react";

import {
  type AgentChatResponse,
  type StudentProfile,
  fetchProfiles,
  fetchTrace,
  sendAgentMessage,
} from "@/lib/api";
import { WeeklySchedule } from "@/components/weekly-schedule";

const DEFAULT_PROMPT =
  "Quiero tomar Base de Datos II, Calidad de Software y Org. y Arq. de Computadora. Solo puedo despues de las 5 p.m. y no puedo viernes.";

export function Dashboard() {
  const [profiles, setProfiles] = useState<StudentProfile[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<string>("student_software_01");
  const [term, setTerm] = useState("2026-1");
  const [message, setMessage] = useState(DEFAULT_PROMPT);
  const [lastSubmittedMessage, setLastSubmittedMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<AgentChatResponse | null>(null);
  const [trace, setTrace] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProfiles()
      .then(setProfiles)
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    setResponse(null);
    setTrace([]);
    setError(null);
    setLastSubmittedMessage(null);
  }, [selectedStudent, term]);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      setError("Escribe una solicitud antes de ejecutar el agente.");
      return;
    }
    setLoading(true);
    setError(null);
    setResponse(null);
    setTrace([]);
    setLastSubmittedMessage(trimmedMessage);
    try {
      const result = await sendAgentMessage({
        student_id: selectedStudent,
        message: trimmedMessage,
        term,
      });
      setResponse(result);
      const traceRows = await fetchTrace(result.session_id);
      setTrace(traceRows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ocurrió un error inesperado.");
    } finally {
      setLoading(false);
    }
  }

  const selectedProfile = useMemo(
    () => profiles.find((profile) => profile.student_id === selectedStudent),
    [profiles, selectedStudent],
  );
  const warningItems = response
    ? [...new Set([...response.warnings, ...response.validation_report.warnings])]
    : [];
  const requestedSubjects = Array.isArray(response?.memory_snapshot.desired_subjects)
    ? response.memory_snapshot.desired_subjects.length
    : 0;
  const includedSubjects = response?.recommended_schedule?.chosen_enrollments?.length ?? 0;
  const hasPartialCoverage = Boolean(response) && requestedSubjects > 0 && includedSubjects < requestedSubjects;
  const recommendationStatus = (() => {
    if (response?.human_review) {
      return "Escalado a humano";
    }
    if (!response) {
      return "Recomendación local";
    }
    if (includedSubjects === 0) {
      return "Sin combinación";
    }
    if (hasPartialCoverage) {
      return "Alternativa parcial";
    }
    return "Horario completo";
  })();

  return (
    <div className="page-shell">
      <section className="hero">
        <div className="hero-copy">
          <h1>UTP Schedule Agent Lab</h1>
          <p>
            Un dashboard para ver cómo el agente interpreta restricciones, usa tools,
            valida reglas y decide cuándo escalar a una persona.
          </p>
        </div>
        <div className="hero-badge">Ingeniería de Agentes para UTP</div>
      </section>

      <section className="dashboard">
        <div className="stack">
          <article className="panel">
            <div className="panel-header">
              <h2>Chat del estudiante</h2>
              <span className="pill">{response?.session_id ?? "Nueva sesión"}</span>
            </div>
            <div className="panel-body">
              <form className="chat-form" onSubmit={onSubmit}>
                <div className="control-row inline">
                  <label>
                    Perfil sintético
                    <select value={selectedStudent} onChange={(event) => setSelectedStudent(event.target.value)}>
                      {profiles.map((profile) => (
                        <option key={profile.student_id} value={profile.student_id}>
                          {profile.name} · {profile.current_province}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Periodo
                    <input value={term} onChange={(event) => setTerm(event.target.value)} />
                  </label>
                </div>

                <label>
                  Solicitud
                  <textarea value={message} onChange={(event) => setMessage(event.target.value)} />
                </label>

                <div className="control-row inline">
                  <button className="primary-button" disabled={loading} type="submit">
                    {loading ? "Procesando..." : "Ejecutar agente"}
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => setMessage(DEFAULT_PROMPT)}
                  >
                    Cargar ejemplo
                  </button>
                </div>

                {lastSubmittedMessage ? (
                  <div className="request-preview-card">
                    <strong>Solicitud enviada</strong>
                    <p>{lastSubmittedMessage}</p>
                  </div>
                ) : null}
              </form>
            </div>
          </article>

          <article className="panel">
            <div className="panel-header">
              <h2>Memoria y validación</h2>
              <span className="pill">
                {selectedProfile ? `${selectedProfile.max_credits} créditos max.` : "Perfil"}
              </span>
            </div>
            <div className="panel-body stack">
              <div>
                <h3>Memoria de sesión</h3>
                {response ? (
                  <ul className="memory-list">
                    {Object.entries(response.memory_snapshot).map(([key, value]) => (
                      <li key={key} className="course-card">
                        <strong>{key}</strong>
                        <span>{Array.isArray(value) ? value.join(", ") || "[]" : String(value ?? "—")}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty">Aquí aparecerán preferencias reutilizables y seguras.</p>
                )}
              </div>

              <div>
                <h3>Hard constraints</h3>
                {response ? (
                  <div className="key-value">
                    {Object.entries(response.validation_report.hard_constraints).map(([key, value]) => (
                      <div key={key}>
                        <strong>{key}</strong>
                        <div className={value ? "metric-good" : "metric-danger"}>
                          {value ? "PASS" : "FAIL"}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty">La validación aparece después de ejecutar la recomendación.</p>
                )}
              </div>

              <div>
                <h3>Alertas</h3>
                {warningItems.length ? (
                  <ul className="warning-list">
                    {warningItems.map((warning) => (
                      <li key={warning} className="metric-warn">
                        {warning}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty">Sin alertas por ahora.</p>
                )}
              </div>
            </div>
          </article>
        </div>

        <div className="stack">
          <article className="panel">
            <div className="panel-header">
              <h2>Recomendación del agente</h2>
              <span className="pill">{recommendationStatus}</span>
            </div>
            <div className="panel-body stack">
              {error ? <p className="metric-danger">{error}</p> : null}
              {warningItems.length ? (
                <div className="warning-banner">
                  <strong>Advertencia</strong>
                  <ul className="warning-list">
                    {warningItems.map((warning) => (
                      <li key={warning} className="metric-warn">
                        {warning}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {response ? (
                <div className="request-preview-card">
                  <strong>Cobertura</strong>
                  <p>
                    Incluidas {includedSubjects} de {requestedSubjects || includedSubjects} materias solicitadas.
                  </p>
                </div>
              ) : null}
              {lastSubmittedMessage ? (
                <div className="request-preview-card">
                  <strong>Solicitud procesada</strong>
                  <p>{lastSubmittedMessage}</p>
                </div>
              ) : null}
              <div>
                <strong>{response?.assistant_message ?? "Esperando una solicitud."}</strong>
              </div>

              <div>
                <h3>Horario recomendado</h3>
                {response?.recommended_schedule?.chosen_enrollments?.length ? (
                  <WeeklySchedule schedule={response.recommended_schedule} />
                ) : (
                  <p className="empty">No hay horario confirmado todavía.</p>
                )}
              </div>

              <div>
                <h3>Justificación</h3>
                {response ? (
                  <ul className="explanation-list">
                    {response.explanation.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty">La explicación del agente aparecerá aquí.</p>
                )}
              </div>

              <div>
                <h3>Revisión humana</h3>
                {response?.human_review ? (
                  <div className="course-card">
                    <strong>{response.human_review.reason}</strong>
                    <span>
                      {response.human_review.status} · {response.human_review.assigned_role}
                    </span>
                  </div>
                ) : (
                  <p className="empty">No se requirió handoff en esta sesión.</p>
                )}
              </div>
            </div>
          </article>

          <article className="panel">
            <div className="panel-header">
              <h2>Llamadas a tools y trazas</h2>
              <span className="pill">{response?.tool_calls.length ?? 0} tools</span>
            </div>
            <div className="panel-body stack">
              <div>
                <h3>Llamadas a tools</h3>
                {response?.tool_calls.length ? (
                  <ul className="tool-list">
                    {response.tool_calls.map((tool) => (
                      <li key={`${tool.name}-${tool.latency_ms}`} className="tool-card">
                        <strong>{tool.name}</strong>
                        <span>
                          {tool.status} · {tool.latency_ms} ms
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty">Aquí verás el pipeline interno del agente.</p>
                )}
              </div>

              <div>
                <h3>Línea de tiempo de trazas</h3>
                {trace.length ? (
                  <ul className="trace-list">
                    {trace.map((entry, index) => (
                      <li key={`${String(entry.event)}-${index}`} className="trace-card">
                        <strong>{String(entry.event)}</strong>
                        <span>{String(entry.timestamp ?? "")}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty">Sin trazas todavía.</p>
                )}
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  );
}
