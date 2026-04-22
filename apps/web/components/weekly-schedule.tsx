"use client";

import { useRef, useState } from "react";

import { toPng } from "html-to-image";
import jsPDF from "jspdf";

import type { AgentChatResponse } from "@/lib/api";

const DAY_ORDER = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"];

const DAY_LABELS: Record<string, string> = {
  MONDAY: "Lunes",
  TUESDAY: "Martes",
  WEDNESDAY: "Miércoles",
  THURSDAY: "Jueves",
  FRIDAY: "Viernes",
  SATURDAY: "Sábado",
  SUNDAY: "Domingo",
};

const SESSION_LABELS: Record<string, string> = {
  Theory: "Teoría",
  Laboratory: "Laboratorio",
};

type SchedulePayload = NonNullable<AgentChatResponse["recommended_schedule"]>;

export function WeeklySchedule({ schedule }: { schedule: SchedulePayload }) {
  const exportRef = useRef<HTMLDivElement>(null);
  const [exporting, setExporting] = useState<"png" | "pdf" | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const activeDays = DAY_ORDER.filter((day) =>
    schedule.schedule.some((item) => item.day === day),
  );

  const baseFileName = [
    "horario-utp",
    ...schedule.chosen_enrollments.map((item) => item.subject_id.toLowerCase()),
  ].join("-");

  async function renderScheduleImage(): Promise<{ dataUrl: string; width: number; height: number }> {
    if (!exportRef.current) {
      throw new Error("No encontré el horario para exportar.");
    }

    const dataUrl = await toPng(exportRef.current, {
      cacheBust: true,
      pixelRatio: 2,
      backgroundColor: "#fdf8ef",
    });

    const image = new Image();
    image.src = dataUrl;
    await new Promise<void>((resolve, reject) => {
      image.onload = () => resolve();
      image.onerror = () => reject(new Error("No pude preparar la imagen del horario."));
    });

    return {
      dataUrl,
      width: image.width,
      height: image.height,
    };
  }

  function downloadDataUrl(dataUrl: string, fileName: string) {
    const link = document.createElement("a");
    link.href = dataUrl;
    link.download = fileName;
    link.click();
  }

  async function exportAsPng() {
    setExporting("png");
    setExportError(null);
    try {
      const image = await renderScheduleImage();
      downloadDataUrl(image.dataUrl, `${baseFileName}.png`);
    } catch (error) {
      setExportError(error instanceof Error ? error.message : "No pude exportar el horario como imagen.");
    } finally {
      setExporting(null);
    }
  }

  async function exportAsPdf() {
    setExporting("pdf");
    setExportError(null);
    try {
      const image = await renderScheduleImage();
      const orientation = image.width >= image.height ? "landscape" : "portrait";
      const pdf = new jsPDF({
        orientation,
        unit: "px",
        format: [image.width, image.height],
      });
      pdf.addImage(image.dataUrl, "PNG", 0, 0, image.width, image.height);
      pdf.save(`${baseFileName}.pdf`);
    } catch (error) {
      setExportError(error instanceof Error ? error.message : "No pude exportar el horario como PDF.");
    } finally {
      setExporting(null);
    }
  }

  return (
    <div className="stack">
      <div className="schedule-actions">
        <div className="schedule-summary">
          <span className="pill">Tiempo muerto total: {schedule.total_idle_minutes} min</span>
          <span className="pill">Bloques: {schedule.schedule.length}</span>
        </div>
        <div className="schedule-export-buttons">
          <button
            className="secondary-button"
            type="button"
            onClick={exportAsPng}
            disabled={exporting !== null}
          >
            {exporting === "png" ? "Exportando PNG..." : "Exportar PNG"}
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={exportAsPdf}
            disabled={exporting !== null}
          >
            {exporting === "pdf" ? "Exportando PDF..." : "Exportar PDF"}
          </button>
        </div>
      </div>

      {exportError ? <p className="metric-danger">{exportError}</p> : null}

      <div className="schedule-export-shell" ref={exportRef}>
        <div className="schedule-export-header">
          <h3>Horario semanal recomendado</h3>
          <p>Vista semanal basada en los bloques seleccionados por el agente.</p>
        </div>

        <div className="weekly-schedule">
          {activeDays.map((day) => {
            const items = schedule.schedule
              .filter((item) => item.day === day)
              .sort((left, right) => left.start_time.localeCompare(right.start_time));

            return (
              <section key={day} className="day-column">
                <header className="day-column-header">{DAY_LABELS[day] ?? day}</header>
                <div className="day-column-body">
                  {items.map((item) => (
                    <article
                      key={`${day}-${item.subject_id}-${item.start_time}-${item.session_type}`}
                      className="schedule-block"
                    >
                      <div className="schedule-time">
                        {item.start_time} - {item.end_time}
                      </div>
                      <strong>{item.subject_name}</strong>
                      <div>{SESSION_LABELS[item.session_type] ?? item.session_type}</div>
                      <div>{item.classroom}</div>
                    </article>
                  ))}
                </div>
              </section>
            );
          })}
        </div>

        <div>
          <h3>Materias incluidas</h3>
          <ul className="course-list">
            {schedule.chosen_enrollments.map((item) => (
              <li key={`${item.subject_id}-${item.group_code}`} className="course-card">
                <strong>
                  {item.subject_name} · Grupo {item.group_code}
                </strong>
                <span>
                  {item.subject_id} · {item.hour_code}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
