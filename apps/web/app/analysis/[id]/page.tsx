"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAnalysisStore } from "@/lib/sse-store";
import { RiskOverview } from "@/components/panels/risk-overview";
import { ReportPanel } from "@/components/panels/report";
import { EvidencePanel } from "@/components/panels/evidence";
import { StepBar } from "@/components/step-bar";
import { GRADE_LABEL, RISK_COLORS } from "@/lib/utils";

export default function AnalysisPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const { connect, reset, stage, message, status, entityName, scores, report, signals, articles, error } =
    useAnalysisStore();

  useEffect(() => {
    if (params.id) connect(params.id);
    return () => reset();
  }, [params.id, connect, reset]);

  return (
    <main className="mx-auto max-w-7xl space-y-4 px-4 py-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/")}
            className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm text-[var(--color-muted)] hover:bg-slate-50"
          >
            ← 返回首页
          </button>
          <h1 className="text-xl font-bold">{entityName ?? "分析中…"}</h1>
          {scores && !scores.insufficient_data && (
            <span
              className="rounded px-2 py-0.5 text-xs font-medium text-white"
              style={{ background: RISK_COLORS[scores.grade] }}
            >
              {GRADE_LABEL[scores.grade] ?? scores.grade}
            </span>
          )}
          {scores?.insufficient_data && (
            <span className="rounded bg-slate-200 px-2 py-0.5 text-xs text-[var(--color-muted)]">
              信息不足
            </span>
          )}
        </div>
      </header>

      <StepBar stage={stage} message={message} status={status} />

      {error && (
        <div className="panel px-4 py-3 text-sm text-[var(--color-risk-high)]">
          分析出错：{error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <section className="panel p-4 lg:col-span-5">
          <h2 className="mb-3 text-sm font-semibold text-[var(--color-muted)]">风险总览</h2>
          <RiskOverview scores={scores} />
        </section>
        <section className="panel p-4 lg:col-span-7">
          <h2 className="mb-3 text-sm font-semibold text-[var(--color-muted)]">AI 风险研报</h2>
          <ReportPanel report={report} />
        </section>
      </div>

      <section className="panel p-4">
        <h2 className="mb-3 text-sm font-semibold text-[var(--color-muted)]">
          评分依据 · 关键舆情
        </h2>
        <EvidencePanel signals={signals} articles={articles} />
      </section>

      <footer className="pt-4 text-center text-xs text-[var(--color-muted)]">
        由公开信息与 AI 分析生成，仅供参考，不构成投资建议。
      </footer>
    </main>
  );
}
