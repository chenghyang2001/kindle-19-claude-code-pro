# 練習 02 解答 — 核心元件實作

## 任務 1：Hero Section

### `components/HeroSection.tsx`（Server Component）

```tsx
import { CTAButton } from "./CTAButton";

export function HeroSection() {
  return (
    <section className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 text-white">
      <div className="mx-auto max-w-7xl px-6 py-20 grid grid-cols-1 items-center gap-12 md:grid-cols-2 md:py-32">
        <div className="text-center md:text-left">
          <h1 className="text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
            把點子變成產品，<br className="hidden sm:block" />只要一個下午
          </h1>
          <p className="mt-6 text-lg text-indigo-100 sm:text-xl">
            專為獨立開發者打造的全端工具，從想法到上線，省下 90% 重複工作。
          </p>
          <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:justify-center md:justify-start">
            <CTAButton variant="primary">免費試用</CTAButton>
            <CTAButton variant="secondary">查看 Demo</CTAButton>
          </div>
        </div>
        <div className="hidden md:block">
          <div className="aspect-video rounded-2xl bg-white/10 backdrop-blur-sm ring-1 ring-white/20 shadow-2xl" />
        </div>
      </div>
    </section>
  );
}
```

### `components/CTAButton.tsx`（共用按鈕，含 hover 動畫）

```tsx
type Props = { variant: "primary" | "secondary"; children: React.ReactNode };

export function CTAButton({ variant, children }: Props) {
  const base =
    "rounded-lg px-6 py-3 font-semibold transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg active:translate-y-0";
  const styles = {
    primary: "bg-white text-indigo-700 hover:bg-indigo-50",
    secondary: "border border-white/60 text-white hover:bg-white/10",
  };
  return <button className={`${base} ${styles[variant]}`}>{children}</button>;
}
```

### 任務 1 關鍵設計

| 要求 | class |
|------|-------|
| 手機單欄 / 桌面雙欄 | `grid-cols-1 md:grid-cols-2` |
| 背景漸層（3 色）| `bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500` |
| 按鈕 hover 動畫 | `transition-all hover:-translate-y-0.5 hover:shadow-lg` |
| 字級響應式 | `text-4xl sm:text-5xl lg:text-6xl` |
| 共用 CTA | 抽成 `CTAButton`，`variant` prop 切換 |

非顯而易見細節：`max-w-7xl mx-auto` 限制大螢幕行寬；右欄 `hidden md:block` 手機隱藏（mobile-first）；CTA 群組 `flex-col sm:flex-row` 手機直疊。

## 任務 2：Pricing Table

### `components/PricingSection.tsx`（Server Component，資料驅動）

```tsx
type Plan = {
  name: string;
  price: string;
  period?: string;
  features: string[];
  cta: { label: string; href: string };
  highlighted?: boolean;
};

const plans: Plan[] = [
  { name: "Free", price: "$0", period: "/月", features: ["基本功能", "限 3 個專案", "社群支援"], cta: { label: "免費開始", href: "/signup" } },
  { name: "Pro", price: "$29", period: "/月", features: ["無限專案", "優先支援", "進階分析", "團隊協作"], cta: { label: "免費試用", href: "/signup?plan=pro" }, highlighted: true },
  { name: "Enterprise", price: "聯絡我們", features: ["自訂方案", "SLA 保證", "專屬客戶經理", "SSO / 稽核"], cta: { label: "聯絡銷售", href: "mailto:sales@example.com" } },
];

export function PricingSection() {
  return (
    <section className="bg-gray-50 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <h2 className="text-center text-3xl font-bold sm:text-4xl">選擇適合你的方案</h2>
        <div className="mt-12 grid grid-cols-1 gap-8 md:grid-cols-3 md:items-center">
          {plans.map((plan) => <PricingCard key={plan.name} plan={plan} />)}
        </div>
      </div>
    </section>
  );
}

function PricingCard({ plan }: { plan: Plan }) {
  return (
    <div className={`relative rounded-2xl bg-white p-8 shadow-sm ${plan.highlighted ? "ring-2 ring-indigo-500 shadow-xl md:scale-105" : "ring-1 ring-gray-200"}`}>
      {plan.highlighted && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-indigo-500 px-4 py-1 text-sm font-semibold text-white">最受歡迎</span>
      )}
      <h3 className="text-xl font-bold">{plan.name}</h3>
      <p className="mt-4">
        <span className="text-4xl font-extrabold">{plan.price}</span>
        {plan.period && <span className="text-gray-500">{plan.period}</span>}
      </p>
      <ul className="mt-6 space-y-3">
        {plan.features.map((f) => (
          <li key={f} className="flex items-center gap-2 text-gray-700"><span className="text-indigo-500">✓</span> {f}</li>
        ))}
      </ul>
      <a href={plan.cta.href} className={`mt-8 block rounded-lg py-3 text-center font-semibold transition-colors ${plan.highlighted ? "bg-indigo-600 text-white hover:bg-indigo-700" : "border border-gray-300 text-gray-800 hover:bg-gray-50"}`}>
        {plan.cta.label}
      </a>
    </div>
  );
}
```

### 任務 2 關鍵設計

| 要求 | 做法 |
|------|------|
| 資料驅動（不複製貼上）| `plans` 陣列 + `.map()` |
| Pro 視覺突出 | `ring-2 ring-indigo-500` + `md:scale-105` + `absolute` 推薦徽章 |
| 手機垂直堆疊 | `grid-cols-1 md:grid-cols-3` |
| Enterprise mailto | `href: "mailto:sales@example.com"` |

細節：`md:items-center` 配 Pro 的 `md:scale-105` → 放大時上下置中不頂出；手機單欄不套 scale 避免擠壓。

## 延伸思考：Pricing 從 API 動態載入（多幣別）

1. **資料來源外移**：`plans` 改從 API 拿（Server Component 直接 `await fetch()` 最佳，SEO 友善無 loading 閃爍；或 Client 用 React Query）
2. **元件職責分離**：`PricingCard` 維持純展示（props-driven），**完全不用改** — 只有「資料怎麼來」變了
3. **幣別邏輯**：依地區（`headers()` geo / IP）決定 currency；price 改結構化 `{ amount, currency }` + `Intl.NumberFormat` 格式化
4. **快取**：價格不常變 → `next: { revalidate: 3600 }` 避免每次打 API

**核心觀念**：一開始就把 `PricingCard` 設計成 props-driven 展示元件，從「寫死」換成「API 動態」時卡片元件一行不用改，只改資料來源層 — 這就是良好元件邊界的價值。
