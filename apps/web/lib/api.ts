const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export interface AnalysisCreate {
  query: string;
  days?: number;
  language?: "zh" | "en" | "auto";
  region?: string | null;
}

export interface AnalysisCreated {
  id: string;
  status: string;
}

export async function createAnalysis(
  req: AnalysisCreate
): Promise<AnalysisCreated> {
  const res = await fetch(`${API_BASE}/analyses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`createAnalysis failed: ${res.status}`);
  return res.json();
}

export function sseUrl(taskId: string): string {
  return `${API_BASE}/analyses/${taskId}/events`;
}
