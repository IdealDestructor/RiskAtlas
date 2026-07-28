"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { RadarChart, GaugeChart, BarChart, PieChart, LineChart } from "echarts/charts";
import {
  TooltipComponent,
  GridComponent,
  LegendComponent,
  RadarComponent,
  GraphicComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  RadarChart, GaugeChart, BarChart, PieChart, LineChart,
  TooltipComponent, GridComponent, LegendComponent, RadarComponent, GraphicComponent,
  CanvasRenderer,
]);

export function useECharts(option: echarts.EChartsCoreOption, deps: unknown[] = []) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    if (!chartRef.current) chartRef.current = echarts.init(ref.current);
    chartRef.current.setOption(option, true);
    const onResize = () => chartRef.current?.resize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, deps);

  useEffect(() => {
    return () => {
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, []);

  return ref;
}

export { echarts };
