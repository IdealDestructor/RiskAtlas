"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Search } from "lucide-react";
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
    if (!query.trim()) return;
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
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col items-center justify-center gap-8 px-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">RiskAtlas</h1>
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
              className={`rounded-md px-3 py-1 ${days === d ? "bg-slate-900 text-white" : "bg-slate-100"}`}
            >
              {d} 天
            </button>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="h-12 w-full rounded-lg bg-slate-900 text-white font-medium disabled:opacity-50"
        >
          {loading ? "创建中…" : "开始分析"}
        </button>
        {err && <p className="text-sm text-[var(--color-risk-high)]">{err}</p>}
      </form>

      <div className="flex flex-wrap justify-center gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => setQuery(ex)}
            className="rounded-full border border-[var(--color-border)] px-3 py-1 text-sm text-[var(--color-muted)] hover:bg-slate-50"
          >
            {ex}
          </button>
        ))}
      </div>
    </main>
  );
}
