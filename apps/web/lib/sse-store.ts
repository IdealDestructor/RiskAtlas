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

export interface ArticleRef {
  index: number;
  title: string;
  url: string;
  domain: string;
  snippet?: string | null;
  published_at?: string | null;
}

export interface SignalPayload {
  signal_id: string;
  dimension: string;
  label: string;
  severity: number;
  confidence: number;
  summary: string;
  first_seen: string;
  last_seen: string;
  mention_count: number;
  article_indices: number[];
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
  signals: SignalPayload[];
  articles: ArticleRef[];
  status: string;
  error: string | null;
  connect: (taskId: string) => void;
  reset: () => void;
}

function log(type: "info" | "warn" | "error", tag: string, ...args: unknown[]) {
  const fn = type === "error" ? console.error : type === "warn" ? console.warn : console.info;
  fn(`[舆图][${tag}]`, ...args);
}

function safeParse(raw: string): Record<string, unknown> | null {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
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
  signals: [],
  articles: [],
  status: "pending",
  error: null,

  reset: () =>
    set({
      taskId: null, stage: null, message: null, entityName: null,
      entityType: null, expandedQueries: [], retrievalStats: null,
      scores: null, report: "", signals: [], articles: [],
      status: "pending", error: null,
    }),

  connect: (taskId: string) => {
    set({ taskId, status: "pending", report: "", signals: [], articles: [], error: null });
    const url = sseUrl(taskId);
    log("info", "SSE", `连接事件流开始，taskId=${taskId} url=${url}`);
    const es = new EventSource(url);

    es.onopen = () => {
      log("info", "SSE", `连接已建立 readyState=${es.readyState}（0=连接中 1=已连接 2=关闭）`);
    };

    es.addEventListener("status", (e) => {
      const d = safeParse(e.data);
      log("info", "SSE:status", d ?? e.data);
      if (!d) return;
      set({ stage: d.stage as string, message: d.message as string, status: d.stage as string });
    });
    es.addEventListener("entity", (e) => {
      const d = safeParse(e.data);
      log("info", "SSE:entity", d ?? e.data);
      if (!d) return;
      set({
        entityName: d.entity_name as string,
        entityType: d.entity_type as string,
        expandedQueries: (d.expanded_queries as string[]) ?? [],
      });
    });
    es.addEventListener("retrieval_stats", (e) => {
      const d = safeParse(e.data);
      log("info", "SSE:retrieval_stats", d ?? e.data);
      if (!d) return;
      set({ retrievalStats: d as AnalysisState["retrievalStats"] });
    });
    es.addEventListener("article_analyzed", (e) => {
      const d = safeParse(e.data);
      if (d) log("info", "SSE:article_analyzed", `进度 ${d.done}/${d.total}`, d.current);
    });
    es.addEventListener("scores", (e) => {
      const d = safeParse(e.data);
      log("info", "SSE:scores", d ?? e.data);
      if (!d) return;
      set({ scores: d as unknown as ScoresPayload });
    });
    es.addEventListener("articles", (e) => {
      const d = safeParse(e.data);
      log("info", "SSE:articles", `收到 ${(d?.articles as unknown[] | undefined)?.length ?? 0} 篇文章元数据`);
      if (!d) return;
      set({ articles: (d.articles as unknown as ArticleRef[]) ?? [] });
    });
    es.addEventListener("signal", (e) => {
      const d = safeParse(e.data);
      log("info", "SSE:signal", d ?? e.data);
      if (!d) return;
      set({ signals: [...get().signals, d as unknown as SignalPayload] });
    });
    es.addEventListener("report_chunk", (e) => {
      const d = safeParse(e.data);
      const chunk = d?.text ?? e.data;
      set({ report: get().report + (typeof chunk === "string" ? chunk : "") });
    });
    es.addEventListener("completed", (e) => {
      const d = safeParse(e.data);
      log("info", "SSE:completed", d ?? "分析完成");
      set({ status: "completed" });
    });
    es.addEventListener("error", ((e: MessageEvent) => {
      // 后端 "error" 事件携带 data；连接级错误无 data
      if (e.data) {
        try {
          const d = JSON.parse(e.data);
          log("error", "SSE:error", d);
          set({ error: d.message, status: "failed" });
          return;
        } catch {
          /* ignore parse error */
        }
      }
      if (get().status !== "completed") {
        log("error", "SSE:error", `连接中断 readyState=${es.readyState}`);
        set({ error: "连接中断", status: "failed" });
      }
    }) as EventListener);
    es.addEventListener("__eof__", () => {
      log("info", "SSE", "事件流结束，关闭连接");
      es.close();
    });
  },
}));
