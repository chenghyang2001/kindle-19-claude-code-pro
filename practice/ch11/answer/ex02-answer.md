# 練習 02 解答 — 核心元件實作

實際專案在 `landing/`（`npx create-next-app@latest landing --yes` 建立，Next.js 16.4.2 + React 19.3 + Tailwind v4 + TypeScript strict）。

| 檔案 | 內容 |
| --- | --- |
| `landing/components/Hero.tsx` | Hero Section |
| `landing/components/Pricing.tsx` | Pricing Table（含 `PricingCard`） |
| `landing/lib/pricing.ts` | 方案資料與型別、`formatPrice` |
| `landing/app/page.tsx` | 組合兩個元件 |

## 驗收對照

### 任務 1：Hero

| 要求 | 做法 |
| --- | --- |
| h1 至少 5 字 | 「讓團隊協作快十倍」（8 字） |
| 副標一句話 value proposition | 「一個平台整合任務、文件與自動化…」 |
| 主 CTA「免費試用」 | 白底按鈕，`href="#signup"` |
| 次 CTA「查看 Demo」 | 外框按鈕，`href="#demo"` |
| 手機單欄 / 桌面雙欄 | `grid-cols-1 lg:grid-cols-2`，右欄示意圖 `hidden lg:block`；按鈕手機 `flex-col`、`sm:` 起橫排 |
| 背景漸層 ≥ 2 色 | `bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500`（3 色） |
| 按鈕 hover 動畫 | `transition hover:-translate-y-0.5 hover:scale-105 hover:shadow-xl` |
| ARIA | `<section aria-labelledby="hero-title">`、裝飾圖 `aria-hidden`、按鈕有 `focus-visible` 外框 |

### 任務 2：Pricing

| 要求 | 做法 |
| --- | --- |
| 3 方案 Free $0 / Pro $29 / Enterprise 聯絡我們 | 資料在 `lib/pricing.ts`，`monthlyPrice: null` 顯示「聯絡我們」 |
| Pro 突出 | 「最受歡迎」標籤 + `border-2 border-indigo-600` + 陰影 + `md:scale-105` |
| 手機垂直堆疊 | `grid-cols-1 md:grid-cols-3` |
| Enterprise CTA「聯絡銷售」→ mailto | `mailto:sales@example.com?subject=Enterprise 方案洽詢`（範例信箱） |
| ARIA | 方案用 `<ul>/<li aria-labelledby>`、功能清單 `aria-label`、勾勾 `aria-hidden`、CTA 有描述性 `aria-label` |
| 空資料 | `plans` 為空陣列時顯示 `role="status"` 的「目前沒有可用的方案」 |

### 三寬度目視檢查

截圖在 `answer/screenshots/`（用 Playwright 內附的 chrome-headless-shell 截，因為一般 Chrome headless 在 Windows 最小視窗寬度是 500px，375 會失真）：

- `landing-375.png`：Hero 單欄置中、兩顆按鈕全寬直排；三張方案卡垂直堆疊
- `landing-768.png`：Hero 單欄、按鈕橫排；方案卡三欄並排，Pro 放大突出
- `landing-1280.png`：Hero 左文字右示意圖雙欄；方案卡三欄

## 延伸思考：Pricing 資料改由 API 動態載入（依地區顯示幣別）

1. **資料與呈現已分離**：`Pricing` 透過 `plans` prop 接資料、`PricingPlan` 型別帶 `currency`，`formatPrice` 用 `Intl.NumberFormat`，換幣別不必改元件。
2. **在 Server Component 取資料**：把 `page.tsx` 改成 `async`，在伺服器端讀取地區（例如 `headers()` 的地理位置標頭或 cookie），呼叫定價 API 後把結果傳給 `<Pricing plans={...} />`。瀏覽器不必多一趟請求，也不會閃一下預設價格。
3. **快取策略**：價格依地區變動，頁面就不再是完全靜態；用 Next.js 的快取機制依「地區」做 key 快取（例如每小時重新驗證），避免每次請求都打 API。
4. **載入與錯誤狀態**：用 `<Suspense fallback={<PricingSkeleton />}>` 包住 Pricing，讓 Hero 先出；API 失敗時退回靜態 `PRICING_PLANS`（USD）並記 log，不讓整頁壞掉。
5. **資料驗證**：API 回傳用 Zod 驗證成 `PricingPlan[]`，欄位缺失時當作失敗處理。
6. **使用者手動切換幣別**：若要讓使用者自己選，才需要一個小的 Client Component（`CurrencySelector`），把選擇寫進 cookie 或 URL 參數，再由伺服器重新渲染；卡片本身仍維持 Server Component。
7. **價格語意**：API 應回傳最小單位整數（如 cents）+ ISO 幣別碼，避免浮點誤差；年繳折扣等計算也放在伺服器端。

## 元件程式碼

### `landing/lib/pricing.ts`

```ts
/** 定價方案資料：與元件分離，之後改成 API 動態載入時只需替換資料來源 */
export type PricingPlan = {
  id: "free" | "pro" | "enterprise";
  name: string;
  /** null 代表「聯絡我們」，不顯示數字價格 */
  monthlyPrice: number | null;
  currency: string;
  description: string;
  features: string[];
  cta: { label: string; href: string };
  isRecommended: boolean;
};

export const PRICING_PLANS: PricingPlan[] = [
  {
    id: "free",
    name: "Free",
    monthlyPrice: 0,
    currency: "USD",
    description: "個人試用，快速上手",
    features: ["基本功能", "限 3 個專案", "社群支援"],
    cta: { label: "免費開始", href: "#signup" },
    isRecommended: false,
  },
  {
    id: "pro",
    name: "Pro",
    monthlyPrice: 29,
    currency: "USD",
    description: "成長中的團隊首選",
    features: ["無限專案", "優先支援", "進階分析報表"],
    cta: { label: "升級 Pro", href: "#signup" },
    isRecommended: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    monthlyPrice: null,
    currency: "USD",
    description: "大型組織的客製方案",
    features: ["自訂整合與部署", "SLA 保證", "專屬客戶經理"],
    cta: {
      label: "聯絡銷售",
      href: "mailto:sales@example.com?subject=Enterprise%20%E6%96%B9%E6%A1%88%E6%B4%BD%E8%A9%A2",
    },
    isRecommended: false,
  },
];

export function formatPrice(plan: PricingPlan): string {
  if (plan.monthlyPrice === null) return "聯絡我們";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: plan.currency,
    maximumFractionDigits: 0,
  }).format(plan.monthlyPrice);
}
```

### `landing/components/Hero.tsx`

```tsx
/** Hero 區塊：Server Component（純靜態，無狀態） */
export default function Hero() {
  return (
    <section
      aria-labelledby="hero-title"
      className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 text-white"
    >
      <div className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-12 px-6 py-20 md:py-28 lg:grid-cols-2">
        <div className="text-center lg:text-left">
          <p className="mb-4 inline-block rounded-full bg-white/15 px-3 py-1 text-sm font-medium">
            全新 2.0 版上線
          </p>
          <h1
            id="hero-title"
            className="text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl lg:text-6xl"
          >
            讓團隊協作快十倍
          </h1>
          <p className="mt-6 text-lg text-white/85 sm:text-xl">
            一個平台整合任務、文件與自動化，把重複工作交給系統，專注在真正重要的事。
          </p>
          <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:justify-center lg:justify-start">
            <a
              href="#signup"
              className="rounded-lg bg-white px-6 py-3 text-center font-semibold text-indigo-700 shadow-lg transition duration-200 hover:-translate-y-0.5 hover:scale-105 hover:shadow-xl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              免費試用
            </a>
            <a
              href="#demo"
              className="rounded-lg border-2 border-white/80 px-6 py-3 text-center font-semibold text-white transition duration-200 hover:-translate-y-0.5 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              查看 Demo
            </a>
          </div>
        </div>

        {/* 裝飾用產品示意圖，對螢幕閱讀器隱藏；桌面才顯示形成雙欄 */}
        <div aria-hidden="true" className="hidden lg:block">
          <div className="rounded-2xl bg-white/10 p-6 shadow-2xl ring-1 ring-white/20 backdrop-blur">
            <div className="mb-4 flex gap-2">
              <span className="h-3 w-3 rounded-full bg-red-400" />
              <span className="h-3 w-3 rounded-full bg-yellow-300" />
              <span className="h-3 w-3 rounded-full bg-green-400" />
            </div>
            <div className="space-y-3">
              <div className="h-4 w-3/4 rounded bg-white/40" />
              <div className="h-4 w-1/2 rounded bg-white/30" />
              <div className="grid grid-cols-3 gap-3 pt-4">
                <div className="h-20 rounded-lg bg-white/25" />
                <div className="h-20 rounded-lg bg-white/35" />
                <div className="h-20 rounded-lg bg-white/25" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

### `landing/components/Pricing.tsx`

```tsx
/** Pricing 區塊：Server Component，資料由 props 注入（預設用靜態方案） */
import { PRICING_PLANS, formatPrice, type PricingPlan } from "@/lib/pricing";

type PricingProps = {
  plans?: PricingPlan[];
};

function PricingCard({ plan }: { plan: PricingPlan }) {
  const titleId = `plan-${plan.id}-title`;
  const isMailto = plan.cta.href.startsWith("mailto:");

  return (
    <li
      aria-labelledby={titleId}
      className={`relative flex flex-col rounded-2xl bg-white p-8 text-slate-900 ${
        plan.isRecommended
          ? "border-2 border-indigo-600 shadow-xl md:-translate-y-2 md:scale-105"
          : "border border-slate-200 shadow-sm"
      }`}
    >
      {plan.isRecommended && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-indigo-600 px-3 py-1 text-xs font-semibold text-white">
          最受歡迎
        </span>
      )}
      <h3 id={titleId} className="text-xl font-bold">
        {plan.name}
      </h3>
      <p className="mt-2 text-sm text-slate-600">{plan.description}</p>
      <p className="mt-6">
        <span className="text-4xl font-extrabold">{formatPrice(plan)}</span>
        {plan.monthlyPrice !== null && (
          <span className="text-slate-500"> / 月</span>
        )}
      </p>
      <ul
        className="mt-6 flex-1 space-y-3"
        aria-label={`${plan.name} 方案功能`}
      >
        {plan.features.map((feature) => (
          <li key={feature} className="flex items-start gap-2 text-sm">
            <span aria-hidden="true" className="text-indigo-600">
              ✓
            </span>
            {feature}
          </li>
        ))}
      </ul>
      <a
        href={plan.cta.href}
        aria-label={
          isMailto
            ? `${plan.cta.label}（寄信給業務）`
            : `${plan.cta.label}：${plan.name} 方案`
        }
        className={`mt-8 rounded-lg px-4 py-3 text-center font-semibold transition duration-200 hover:-translate-y-0.5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 ${
          plan.isRecommended
            ? "bg-indigo-600 text-white hover:bg-indigo-700"
            : "bg-slate-100 text-slate-900 hover:bg-slate-200"
        }`}
      >
        {plan.cta.label}
      </a>
    </li>
  );
}

export default function Pricing({ plans = PRICING_PLANS }: PricingProps) {
  return (
    <section aria-labelledby="pricing-title" className="bg-slate-50 px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <h2
          id="pricing-title"
          className="text-center text-3xl font-bold text-slate-900 sm:text-4xl"
        >
          簡單透明的定價
        </h2>
        <p className="mt-4 text-center text-slate-600">
          隨時升級或降級，無綁約
        </p>
        {plans.length === 0 ? (
          <p role="status" className="mt-12 text-center text-slate-500">
            目前沒有可用的方案
          </p>
        ) : (
          <ul className="mt-14 grid grid-cols-1 gap-8 md:grid-cols-3 md:items-stretch">
            {plans.map((plan) => (
              <PricingCard key={plan.id} plan={plan} />
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
```

### `landing/app/page.tsx`

```tsx
import Hero from "@/components/Hero";
import Pricing from "@/components/Pricing";

export default function Home() {
  return (
    <main id="main-content">
      <Hero />
      <Pricing />
    </main>
  );
}
```
