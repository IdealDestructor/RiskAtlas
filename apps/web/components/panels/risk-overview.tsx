"use client";

import { useECharts } from "@/components/charts/use-echarts";
import { DIM_LABELS, GRADE_LABEL, RISK_COLORS } from "@/lib/utils";
import type { ScoresPayload } from "@/lib/sse-store";

export function RiskOverview({ scores }: { scores: ScoresPayload | null }) {
  const overall = scores?.overall ?? 0;
  const gradeColor = (scores && RISK_COLORS[scores.grade]) ?? "var(--color-muted)";
  const radarValues = Object.keys(DIM_LABELS).map((d) => scores?.dimensions[d]?.score ?? 0);

  const gaugeRef = useECharts(
    {
      series: [
        {
          type: "gauge",
          startAngle: 200,
          endAngle: -20,
          min: 0,
          max: 100,
          radius: "100%",
          center: ["50%", "55%"],
          progress: { show: true, width: 16, roundCap: true, color: gradeColor },
          axisLine: { lineStyle: { width: 16, color: [[1, "#e2e8f0"]] } },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          pointer: { show: false },
          detail: {
            valueAnimation: true,
            fontSize: 32,
            fontWeight: "bold",
            offsetCenter: [0, "38%"],
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
        radius: "72%",
        axisName: { color: "#64748b", fontSize: 12 },
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

  if (!scores) {
    return <div className="flex h-64 items-center justify-center text-sm text-[var(--color-muted)]">等待评分数据…</div>;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col items-center gap-2">
        <div ref={gaugeRef} className="h-56 w-56" />
        <div className="flex flex-col items-center gap-1">
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
      <div>
        <div className="mb-1 text-xs font-semibold text-[var(--color-muted)]">六维风险雷达</div>
        <div ref={radarRef} className="h-72 w-full" />
      </div>
    </div>
  );
}
