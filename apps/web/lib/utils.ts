import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export const RISK_COLORS: Record<string, string> = {
  low: "var(--color-risk-low)",
  low_mid: "var(--color-risk-low_mid)",
  mid: "var(--color-risk-mid)",
  mid_high: "var(--color-risk-mid_high)",
  high: "var(--color-risk-high)",
  insufficient: "var(--color-muted)",
};

export const GRADE_LABEL: Record<string, string> = {
  low: "低",
  low_mid: "中低",
  mid: "中",
  mid_high: "中高",
  high: "高",
  insufficient: "信息不足",
};

export const DIM_LABELS: Record<string, string> = {
  judicial: "司法诉讼",
  finance: "财务信用",
  regulatory: "监管合规",
  governance: "经营治理",
  quality: "产品质量",
  reputation: "声誉舆情",
};

export const SEVERITY_COLORS: Record<number, string> = {
  1: "#94a3b8",
  2: "#60a5fa",
  3: "#eab308",
  4: "#f97316",
  5: "#dc2626",
};

export const SEVERITY_LABEL: Record<number, string> = {
  1: "很低",
  2: "较低",
  3: "中等",
  4: "较高",
  5: "很高",
};
