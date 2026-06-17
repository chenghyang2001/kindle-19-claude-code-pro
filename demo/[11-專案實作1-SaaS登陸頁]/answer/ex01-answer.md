# 練習 01 解答 — 元件拆解分析

## 任務 1：元件樹設計

```
LandingPage
├── Navbar ──────────────────── [組合]
│   ├── Logo ───────────────── [葉]
│   ├── NavLinks ───────────── [葉]
│   ├── CTAButton ⭐共用 ────── [葉]
│   └── MobileMenuToggle ───── [葉]
│
├── HeroSection ─────────────── [組合]
│   ├── Headline ───────────── [葉]
│   ├── Subheadline ────────── [葉]
│   ├── CTAButton ⭐共用
│   └── HeroImage ──────────── [葉]
│
├── FeaturesSection ─────────── [組合]
│   └── FeatureCard ×N ⭐重複 ─ [葉]（icon + 標題 + 描述）
│
├── SocialProofSection ──────── [組合]
│   ├── StatItem ×N ────────── [葉]（數字 + 標籤）
│   └── TestimonialCard ×N ──── [葉]
│
├── PricingSection ──────────── [組合]
│   ├── BillingToggle ───────── [葉]（月付/年付切換）
│   └── PricingCard ×N ⭐重複 ── [組合]
│       ├── PlanName / Price ── [葉]
│       ├── FeatureList ─────── [葉]
│       └── CTAButton ⭐共用
│
├── FAQSection ──────────────── [組合]
│   └── FAQItem ×N ──────────── [葉]（手風琴展開）
│
├── CTASection ──────────────── [組合]
│   └── CTAButton ⭐共用
│
└── Footer ──────────────────── [組合]
    ├── FooterLinks ─────────── [葉]
    └── SocialIcons ─────────── [葉]
```

### 三個問題的答案

| 問題 | 答案 |
|------|------|
| 葉節點元件 | `Logo`、`Button`、`FeatureCard`、`StatItem`、`FAQItem`、`NavLinks` 等最小單元 |
| 組合元件 | `Navbar`、`HeroSection`、`PricingSection`、`PricingCard`（卡片本身也是組合）|
| 共用元件 | **`CTAButton`**（出現 4 次以上）最值得抽取；其次 `FeatureCard` / `PricingCard` 是同型重複，用 `.map()` 渲染 |

## 任務 2：Server vs Client 決策表

| 元件 | 類型 | 理由 |
|------|------|------|
| `Navbar` | **Client** | 手機版漢堡選單需要 `useState` 控制開合 |
| `Logo` / `NavLinks` | Server | 純靜態，可獨立成 Server（被 Client 父層包住仍可當 children 傳入）|
| `HeroSection` | **Server** | 靜態文案 + 圖片，無互動 |
| `CTAButton` | **Client** | 有 `onClick`（捲動到定價 / 開 modal / 觸發追蹤事件）|
| `FeaturesSection` | Server | 靜態卡片列表 |
| `SocialProofSection` | Server | 靜態數字與評價 |
| `PricingSection` | **Client** | 含 `BillingToggle` 月付/年付切換狀態 |
| `FAQSection` | **Client** | 手風琴展開需要 `useState` 記錄展開項 |
| `CTASection` | Server（按鈕是 Client）| 區塊本身靜態，只有內嵌的 `CTAButton` 是 Client |
| `Footer` | Server | 純連結與圖示 |

## 核心觀念

1. **「會動的才需要 Client」**：App Router 預設全是 Server Component，只有需要 state / event / browser API 時才標 `"use client"`。
2. **互動下沉（push client down）**：不要整個 `HeroSection` 標 Client，只把 `CTAButton` 標 Client。讓 Client 邊界盡量靠近葉節點，保留最多 Server 渲染效能。
3. **重複即抽取**：看到 `×N` 就是 `.map()` 的訊號，同型卡片抽成單一元件用 props 餵資料。
