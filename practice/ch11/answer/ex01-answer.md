# 練習 01 解答 — 元件拆解分析

## 任務 1：元件樹

```
LandingPage (app/page.tsx)
├── Navbar
│   ├── Logo（共用：Footer 也用）
│   ├── NavLinks
│   │   └── NavLink ×N
│   ├── MobileMenuToggle
│   └── CTAButton（共用）
├── HeroSection
│   ├── Badge（共用：Pricing 的「最受歡迎」也用）
│   ├── Headline
│   ├── Subheadline
│   ├── CTAGroup
│   │   ├── CTAButton variant="primary"（共用）
│   │   └── CTAButton variant="secondary"（共用）
│   └── HeroIllustration
├── FeaturesSection
│   ├── SectionHeading（共用）
│   └── FeatureGrid
│       └── FeatureCard ×3~6
│           ├── Icon（共用）
│           ├── FeatureTitle
│           └── FeatureDescription
├── SocialProofSection
│   ├── SectionHeading（共用）
│   ├── StatsRow
│   │   └── StatItem ×N
│   └── TestimonialList
│       └── TestimonialCard ×N
│           ├── Avatar
│           ├── Quote
│           └── AuthorInfo
├── PricingSection
│   ├── SectionHeading（共用）
│   ├── BillingToggle（月繳 / 年繳，選做）
│   └── PricingGrid
│       └── PricingCard ×3
│           ├── Badge（共用，僅推薦方案）
│           ├── PlanName / PlanDescription
│           ├── PriceTag
│           ├── FeatureList
│           │   └── FeatureListItem（含 Icon）
│           └── CTAButton（共用）
├── FAQSection
│   ├── SectionHeading（共用）
│   └── FAQList
│       └── FAQItem ×N（可展開）
├── CTASection
│   ├── Headline
│   └── CTAButton（共用）
└── Footer
    ├── Logo（共用）
    ├── FooterLinkGroup ×N
    │   └── FooterLink
    └── Copyright
```

### 1. 葉節點元件（最小單元）

`Logo`、`NavLink`、`CTAButton`、`Badge`、`Icon`、`Headline`、`Subheadline`、`FeatureCard`、`StatItem`、`Avatar`、`Quote`、`PriceTag`、`FeatureListItem`、`FAQItem`、`FooterLink`、`Copyright`、`HeroIllustration`。

> `PricingCard`、`TestimonialCard` 嚴格說也由更小元素組成，但實務上把它們當「卡片型葉節點」：只吃一筆資料、不再組合其他卡片。

### 2. 組合元件（由葉節點組成）

`Navbar`、`HeroSection`、`CTAGroup`、`FeaturesSection`、`FeatureGrid`、`SocialProofSection`、`StatsRow`、`TestimonialList`、`PricingSection`、`PricingGrid`、`FAQSection`、`FAQList`、`CTASection`、`Footer`，最上層是 `LandingPage`。

### 3. 值得抽成共用元件的

| 元件 | 出現位置 | 抽取理由 |
| --- | --- | --- |
| `CTAButton`（primary / secondary / outline） | Navbar、Hero ×2、PricingCard ×3、CTASection | 出現 7 次，hover 動畫、focus 樣式、尺寸要一致 |
| `SectionHeading`（標題 + 副標） | Features、SocialProof、Pricing、FAQ | 每個 section 開頭結構相同，也統一 `aria-labelledby` 的 id |
| `Badge` | Hero 的「新版上線」、Pricing 的「最受歡迎」 | 同一種膠囊樣式 |
| `Logo` | Navbar、Footer | 品牌一致 |
| `Icon` | FeatureCard、FeatureListItem、FAQ 展開箭頭 | 統一尺寸與 `aria-hidden` |
| `Container`（max-width + padding） | 所有 section | 版面寬度一致 |

## 任務 2：Server vs Client 決策

| 元件 | 類型 | 理由 |
| --- | --- | --- |
| LandingPage | Server | 只負責排版組合，無狀態 |
| Navbar | Server（外殼）+ Client（`MobileMenuToggle`） | 只有手機選單開合需要 `useState`，把互動切成小的 Client 島，其餘留在 Server |
| MobileMenuToggle | Client | `useState` 控制開合、`onClick` |
| HeroSection | Server | 靜態內容；CTA 是 `<a>` 連結，不需 JS |
| CTAButton | Server | 純連結 + CSS hover；若要埋點追蹤 `onClick` 才改 Client |
| FeaturesSection / FeatureCard | Server | 靜態展示 |
| SocialProofSection | Server | 靜態；若要數字滾動動畫，只把 `AnimatedCounter` 做成 Client |
| TestimonialList | Server（輪播版則 Client） | 靜態列表用 Server；做成自動輪播需要 `useEffect` 計時器 → Client |
| PricingSection | Server | 方案資料在伺服器端取得並渲染 |
| BillingToggle | Client | 月繳／年繳切換需要 `useState` |
| PricingCard | Server | 純展示 props |
| FAQSection | Server | 外殼靜態 |
| FAQItem | Client（或用原生 `<details>` 保持 Server） | 自製展開動畫需 `useState`；用 `<details>/<summary>` 可零 JS |
| CTASection | Server | 靜態 |
| Footer | Server | 靜態 |

**原則：** 預設全部 Server Component，只把真正需要互動的最小元件標成 `"use client"`，減少送到瀏覽器的 JS。

## 實作對照

本次 `landing/` 實際做了 `Hero`（`components/Hero.tsx`）與 `Pricing`（`components/Pricing.tsx`，內含 `PricingCard`），兩者都是 Server Component（檔案沒有 `"use client"`，build 結果首頁為 `○ (Static)`）。
