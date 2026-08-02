"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const TYPING_INTERVAL_MS = 16;
const CHARS_PER_TICK = 2;

/**
 * 打字机效果：目标文本增长时按固定节奏逐字揭示，
 * 避免等待整份研报生成完成才一次性输出。
 */
function useTypewriter(target: string) {
  const [shown, setShown] = useState(0);
  const shownRef = useRef(0);

  useEffect(() => {
    if (target.length <= shownRef.current) return;
    let raf = 0;
    let lastTick = 0;
    const step = (now: number) => {
      if (now - lastTick >= TYPING_INTERVAL_MS) {
        lastTick = now;
        const next = Math.min(target.length, shownRef.current + CHARS_PER_TICK);
        shownRef.current = next;
        setShown(next);
      }
      if (shownRef.current < target.length) {
        raf = requestAnimationFrame(step);
      }
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target]);

  return { text: target.slice(0, shown), done: shown >= target.length };
}

export function ReportPanel({ report }: { report: string }) {
  const { text, done } = useTypewriter(report);

  if (!report) {
    return (
      <div className="space-y-2">
        <div className="h-4 w-3/4 animate-pulse rounded bg-slate-100" />
        <div className="h-4 w-1/2 animate-pulse rounded bg-slate-100" />
        <div className="h-4 w-2/3 animate-pulse rounded bg-slate-100" />
        <p className="pt-2 text-sm text-[var(--color-muted)]">研报生成中…</p>
      </div>
    );
  }

  return (
    <div>
      <div className="prose prose-sm max-w-none text-sm leading-relaxed text-slate-700">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
      </div>
      {!done && (
        <span className="mt-1 inline-block h-4 w-2 animate-pulse bg-slate-400 align-middle" />
      )}
    </div>
  );
}
