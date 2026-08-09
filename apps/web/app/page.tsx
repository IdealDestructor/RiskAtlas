"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Loader2, Search } from "lucide-react";
import { createAnalysis } from "@/lib/api";

const EXAMPLES = ["腾讯", "恒大", "OpenAI", "宁德时代", "字节跳动"];

export default function HomePage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e?: React.FormEvent) {
    e?.preventDefault();
    if (loading || !query.trim()) return;
    setLoading(true);
    setErr(null);
    try {
      const { id } = await createAnalysis({ query: query.trim(), days });
      router.push(`/analysis/${id}`);
    } catch {
      setErr("分析任务创建失败，请检查后端服务是否已启动。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-indigo-100 via-sky-50 to-fuchsia-100 px-4">
      {loading && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/20 px-4 backdrop-blur-[2px]"
          role="status"
          aria-live="polite"
          aria-label="正在创建分析任务"
        >
          <div className="w-full max-w-sm rounded-2xl border border-white/70 bg-white/90 p-6 text-center shadow-2xl shadow-indigo-900/20">
            <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
              <Loader2 className="size-7 animate-spin" aria-hidden="true" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-slate-900">正在准备风险分析</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              正在创建任务并连接数据源，请稍候…
            </p>
            <div className="mt-5 flex items-center justify-center gap-1.5" aria-hidden="true">
              <span className="size-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:-0.3s]" />
              <span className="size-2 animate-bounce rounded-full bg-sky-500 [animation-delay:-0.15s]" />
              <span className="size-2 animate-bounce rounded-full bg-fuchsia-500" />
            </div>
          </div>
        </div>
      )}
      <div className="glow-float-a pointer-events-none absolute -left-24 -top-24 size-96 rounded-full bg-gradient-to-br from-indigo-400 to-sky-300 blur-3xl" />
      <div className="glow-float-b pointer-events-none absolute -right-24 top-1/3 size-[28rem] rounded-full bg-gradient-to-br from-fuchsia-400 to-pink-300 blur-3xl" />
      <div className="glow-float-c pointer-events-none absolute -bottom-32 left-1/4 size-96 rounded-full bg-gradient-to-br from-amber-300 to-orange-300 blur-3xl" />
      <div className="glow-float-d pointer-events-none absolute bottom-1/4 right-1/4 size-64 rounded-full bg-gradient-to-br from-cyan-300 to-emerald-300 blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-2xl flex-col items-center gap-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900" style={{ fontFamily: 'serif' }}>舆图</h1>
          <p className="mt-3 text-base text-[var(--color-muted)]">
            输入公司、品牌或人物，30 秒内生成实时风险画像
          </p>
        </div>

        <form onSubmit={submit} className="w-full space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--color-muted)]" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
              aria-busy={loading}
              placeholder="输入查询词，如公司名称"
              className="h-14 w-full rounded-lg border border-[var(--color-border)] bg-white pl-11 pr-4 text-lg outline-none focus:border-slate-400"
            />
          </div>

          <div className="flex items-center gap-2 text-sm text-[var(--color-muted)]">
            <span>时间窗</span>
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDays(d)}
                disabled={loading}
                className={`rounded-md px-3 py-1 ${days === d ? "bg-slate-900 text-white" : "bg-slate-100"}`}
              >
                {d} 天
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            aria-busy={loading}
            className="h-12 w-full rounded-lg bg-slate-900 font-medium text-white shadow-lg shadow-indigo-500/30 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <span className="inline-flex items-center justify-center gap-2">
                <Loader2 className="size-4 animate-spin" aria-hidden="true" />
                创建分析任务…
              </span>
            ) : (
              "开始分析"
            )}
          </button>
          {err && <p className="text-sm text-[var(--color-risk-high)]">{err}</p>}
        </form>

        <div className="flex flex-wrap justify-center gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => setQuery(ex)}
              disabled={loading}
              className="rounded-full border border-[var(--color-border)] bg-white/70 px-3 py-1 text-sm text-[var(--color-muted)] hover:bg-white"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}
