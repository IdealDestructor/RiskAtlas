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
