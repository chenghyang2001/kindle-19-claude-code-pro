import type { ReactNode } from "react";

export const metadata = { title: "Freelancer Dashboard API" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-TW">
      <body>{children}</body>
    </html>
  );
}
