"use client";

import { create } from "zustand";
import { sseUrl } from "./api";

export interface DimScore {
  dimension: string;
  score: number;
}

export interface ScoresPayload {
  overall: number;
  grade: string;
  dimensions: Record<string, { score: number; raw: number }>;
  insufficient_data: boolean;
  sample_size: number;
}

interface AnalysisState {
  taskId: string | null;
  stage: string | null;
  message: string | null;
  entityName: string | null;
  entityType: string | null;
  expandedQueries: string[];
  retrievalStats: {
    fetched: number;
    after_dedup: number;
    clusters: number;
    sources: { name: string; status: string; count: number }[];
  } | null;
  scores: ScoresPayload | null;
  report: string;
  status: string;
  error: string | null;
  connect: (taskId: string) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set, get) => ({
  taskId: null,
  stage: null,
  message: null,
  entityName: null,
  entityType: null,
  expandedQueries: [],
  retrievalStats: null,
  scores: null,
  report: "",
  status: "pending",
  error: null,

  reset: () =>
    set({
      taskId: null, stage: null, message: null, entityName: null,
      entityType: null, expandedQueries: [], retrievalStats: null,
      scores: null, report: "", status: "pending", error: null,
    }),

  connect: (taskId: string) => {
    set({ taskId, status: "pending", report: "", error: null });
    const url = sseUrl(taskId);
    const es = new EventSource(url);

    es.addEventListener("status", (e) => {
      const d = JSON.parse(e.data);
      set({ stage: d.stage, message: d.message, status: d.stage });
    });
    es.addEventListener("entity", (e) => {
      const d = JSON.parse(e.data);
      set({ entityName: d.entity_name, entityType: d.entity_type, expandedQueries: d.expanded_queries ?? [] });
    });
    es.addEventListener("retrieval_stats", (e) => {
      set({ retrievalStats: JSON.parse(e.data) });
    });
    es.addEventListener("scores", (e) => {
      set({ scores: JSON.parse(e.data) });
    });
    es.addEventListener("report_chunk", (e) => {
      const d = JSON.parse(e.data);
      set({ report: get().report + (d.text ?? "") });
    });
    es.addEventListener("completed", (e) => {
      set({ status: "completed" });
    });
    es.addEventListener("error", ((e: MessageEvent) => {
      // 后端 "error" 事件携带 data；连接级错误无 data
      if (e.data) {
        try {
          const d = JSON.parse(e.data);
          set({ error: d.message, status: "failed" });
          return;
        } catch {
          /* ignore parse error */
        }
      }
      if (get().status !== "completed") {
        set({ error: "连接中断", status: "failed" });
      }
    }) as EventListener);
    es.addEventListener("__eof__", () => {
      es.close();
    });
  },
}));
