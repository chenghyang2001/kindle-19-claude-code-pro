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
