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
