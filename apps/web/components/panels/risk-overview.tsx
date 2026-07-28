"use client";

import { useECharts } from "@/components/charts/use-echarts";
import { GRADE_LABEL, RISK_COLORS } from "@/lib/utils";
import type { ScoresPayload } from "@/lib/sse-store";

const DIM_LABELS: Record<string, string> = {
  judicial: "司法诉讼",
  finance: "财务信用",
  regulatory: "监管合规",
  governance: "经营治理",
  quality: "产品质量",
  reputation: "声誉舆情",
};

export function RiskOverview({ scores }: { scores: ScoresPayload | null }) {
  if (!scores) {
    return <div className="flex h-64 items-center justify-center text-sm text-[var(--color-muted)]">等待评分数据…</div>;
  }

  const overall = scores.overall;
  const gradeColor = RISK_COLORS[scores.grade] ?? "var(--color-muted)";
  const radarValues = Object.keys(DIM_LABELS).map((d) => scores.dimensions[d]?.score ?? 0);

  const gaugeRef = useECharts(
    {
      series: [
        {
          type: "gauge",
          startAngle: 200,
          endAngle: -20,
          min: 0,
          max: 100,
          radius: "90%",
          progress: { show: true, width: 14, roundCap: true, color: gradeColor },
          axisLine: { lineStyle: { width: 14, color: [[1, "#e2e8f0"]] } },
          axisTick: { show: false },
          splitLine: { show: false },
          pointer: { show: false },
          detail: {
            valueAnimation: true,
            fontSize: 28,
            fontWeight: "bold",
            offsetCenter: [0, "0%"],
            formatter: "{value}",
            color: "#0f172a",
          },
          data: [{ value: overall }],
        },
      ],
    },
    [overall, gradeColor]
  );

  const radarRef = useECharts(
    {
      radar: {
        indicator: Object.keys(DIM_LABELS).map((d) => ({ name: DIM_LABELS[d], max: 100 })),
        radius: "65%",
        axisName: { color: "#64748b", fontSize: 11 },
        splitLine: { lineStyle: { color: "#e2e8f0" } },
        splitArea: { show: false },
      },
      series: [
        {
          type: "radar",
          data: [
            {
              value: radarValues,
              areaStyle: { color: "rgba(220, 38, 38, 0.15)" },
              lineStyle: { color: "#dc2626", width: 2 },
              itemStyle: { color: "#dc2626" },
            },
          ],
        },
      ],
    },
    [radarValues.join(",")]
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-4">
        <div ref={gaugeRef} className="h-40 w-40" />
        <div className="space-y-1">
          <div className="text-xs text-[var(--color-muted)]">综合风险分</div>
          <span
            className="inline-block rounded px-2.5 py-1 text-sm font-semibold text-white"
            style={{ background: gradeColor }}
          >
            {GRADE_LABEL[scores.grade] ?? scores.grade}
          </span>
          <div className="text-xs text-[var(--color-muted)]">
            样本量 {scores.sample_size} 篇
          </div>
        </div>
      </div>
      <div ref={radarRef} className="h-56 w-full" />
    </div>
  );
}
