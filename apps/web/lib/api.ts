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
  const url = `${API_BASE}/analyses`;
  console.info(`[舆图][API] POST ${url}`, req);
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    console.info(`[舆图][API] POST ${url} -> ${res.status} ${res.statusText}`);
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      console.error(`[舆图][API] POST ${url} 失败 status=${res.status}`, body);
      throw new Error(`createAnalysis failed: ${res.status}`);
    }
    const data: AnalysisCreated = await res.json();
    console.info(`[舆图][API] POST ${url} 返回`, data);
    return data;
  } catch (err) {
    console.error(`[舆图][API] POST ${url} 异常`, err);
    throw err;
  }
}

export function sseUrl(taskId: string): string {
  return `${API_BASE}/analyses/${taskId}/events`;
}
