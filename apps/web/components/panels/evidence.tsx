"use client";

import { ExternalLink } from "lucide-react";
import {
  DIM_LABELS,
  SEVERITY_COLORS,
  SEVERITY_LABEL,
} from "@/lib/utils";
import type { ArticleRef, SignalPayload } from "@/lib/sse-store";

function formatDate(iso?: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" });
}

export function EvidencePanel({
  signals,
  articles,
}: {
  signals: SignalPayload[];
  articles: ArticleRef[];
}) {
  const articleMap = new Map(articles.map((a) => [a.index, a]));

  if (signals.length === 0) {
    return (
      <p className="text-sm text-[var(--color-muted)]">
        暂无提取到足够的风险信号，评分主要基于样本量判断（信息不足时不会给出有效等级）。
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-[var(--color-muted)]">
        以下为 AI 从公开报道中抽取的风险信号，是各维度评分与综合评分的直接依据，按影响程度排序。
      </p>
      {signals.map((sig) => {
        const refs = (sig.article_indices ?? [])
          .map((i) => articleMap.get(i))
          .filter((a): a is ArticleRef => Boolean(a));
        const color = SEVERITY_COLORS[sig.severity] ?? "#94a3b8";
        return (
          <div key={sig.signal_id} className="rounded-md border border-[var(--color-border)] p-3">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className="rounded px-1.5 py-0.5 text-xs font-medium text-white"
                style={{ background: color }}
              >
                {DIM_LABELS[sig.dimension] ?? sig.dimension} · {SEVERITY_LABEL[sig.severity]}
              </span>
              <span className="text-sm font-medium text-slate-800">{sig.label}</span>
              <span className="ml-auto text-xs text-[var(--color-muted)]">
                {sig.mention_count} 篇提及{sig.first_seen ? ` · 最早 ${formatDate(sig.first_seen)}` : ""}
              </span>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">{sig.summary}</p>
            {refs.length > 0 && (
              <ul className="mt-2 space-y-1.5">
                {refs.slice(0, 3).map((a) => (
                  <li key={a.index}>
                    <a
                      href={a.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group flex items-start gap-1.5 text-sm text-indigo-600 hover:text-indigo-800 hover:underline"
                    >
                      <ExternalLink className="mt-0.5 size-3.5 shrink-0" />
                      <span className="min-w-0">
                        <span className="line-clamp-1">{a.title}</span>
                        {a.snippet && (
                          <span className="line-clamp-2 block text-xs text-[var(--color-muted)]">
                            {a.snippet}
                          </span>
                        )}
                        <span className="text-xs text-[var(--color-muted)]">
                          {a.domain}
                          {a.published_at ? ` · ${formatDate(a.published_at)}` : ""}
                        </span>
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
}
