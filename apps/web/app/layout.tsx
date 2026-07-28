import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RiskAtlas · 实体风险情报",
  description: "LLM 驱动的实时实体风险情报平台",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
