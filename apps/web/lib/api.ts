export type ToolCallRecord = {
  name: string;
  status: string;
  latency_ms: number;
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
};

export type ValidationReport = {
  hard_constraints: Record<string, boolean>;
  warnings: string[];
  metrics: Record<string, number | string | boolean>;
};

export type HumanReviewTicket = {
  status: string;
  reason: string;
  assigned_role: string;
  ticket_id?: string | null;
  payload?: Record<string, unknown>;
};

export type AgentChatResponse = {
  session_id: string;
  assistant_message: string;
  recommended_schedule: {
    chosen_enrollments: Array<{
      subject_id: string;
      subject_name: string;
      group_code: string;
      hour_code: string;
    }>;
    total_idle_minutes: number;
    schedule: Array<{
      day: string;
      subject_id: string;
      subject_name: string;
      session_type: string;
      classroom: string;
      start_time: string;
      end_time: string;
      lab_code?: string | null;
    }>;
  } | null;
  explanation: string[];
  tool_calls: ToolCallRecord[];
  memory_snapshot: Record<string, unknown>;
  validation_report: ValidationReport;
  human_review?: HumanReviewTicket | null;
  warnings: string[];
  plan: string[];
};

export type StudentProfile = {
  student_id: string;
  name: string;
  career: string;
  current_province: string;
  max_credits: number;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchProfiles(): Promise<StudentProfile[]> {
  const response = await fetch(`${API_BASE}/api/v1/student-profiles`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("No pude cargar los perfiles sintéticos.");
  }
  return response.json();
}

export async function sendAgentMessage(payload: {
  session_id?: string;
  student_id: string;
  message: string;
  term: string;
}): Promise<AgentChatResponse> {
  const response = await fetch(`${API_BASE}/api/v1/agent/respond`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("La solicitud al agente falló.");
  }
  return response.json();
}

export async function fetchTrace(sessionId: string): Promise<Array<Record<string, unknown>>> {
  const response = await fetch(`${API_BASE}/api/v1/sessions/${sessionId}/trace`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("No pude cargar las trazas de la sesión.");
  }
  return response.json();
}
