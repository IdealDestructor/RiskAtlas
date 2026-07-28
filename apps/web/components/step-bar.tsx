"use client";

import { Check, Loader2 } from "lucide-react";

const STEPS = [
  { key: "resolving", label: "实体解析" },
  { key: "retrieving", label: "多源检索" },
  { key: "analyzing", label: "AI 分析" },
  { key: "scoring", label: "风险评分" },
  { key: "reporting", label: "生成研报" },
];

export function StepBar({
  stage,
  message,
  status,
}: {
  stage: string | null;
  message: string | null;
  status: string;
}) {
  const order = STEPS.map((s) => s.key);
  const currentIdx = stage ? order.indexOf(stage) : -1;
  const isDone = status === "completed";

  return (
    <div className="panel flex items-center gap-1 px-3 py-2">
      {STEPS.map((s, i) => {
        const done = isDone || (currentIdx > i);
        const active = currentIdx === i && !isDone;
        return (
          <div key={s.key} className="flex items-center gap-1">
            <div
              className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-sm ${
                active ? "bg-slate-900 text-white" : done ? "text-slate-700" : "text-[var(--color-muted)]"
              }`}
            >
              {done ? (
                <Check className="size-4" />
              ) : active ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <span className="size-4 text-center text-xs">{i + 1}</span>
              )}
              {s.label}
            </div>
            {i < STEPS.length - 1 && <span className="text-[var(--color-border)]">›</span>}
          </div>
        );
      })}
      {message && (
        <span className="ml-auto text-xs text-[var(--color-muted)]">{message}</span>
      )}
    </div>
  );
}
