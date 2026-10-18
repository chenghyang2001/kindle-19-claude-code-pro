# 練習 01 — 基礎：元件拆解分析

## 情境說明
你收到一個 SaaS 產品的設計需求，需要在開始寫程式碼前做好架構規劃。

## 典型 SaaS 登陸頁結構

```
Navbar（導覽列）
↓
Hero Section（主標題 + CTA）
↓
Features Section（功能特色，通常 3-6 個）
↓
Social Proof（客戶評價 / 數字）
↓
Pricing Section（定價方案）
↓
FAQ（常見問題）
↓
CTA Section（最後行動呼籲）
↓
Footer（頁腳）
```

## 任務

### 任務 1：元件樹設計
設計完整的元件樹，回答以下問題：

1. 哪些是「葉節點」元件（最小單元，例如 Button、PricingCard）？
2. 哪些是「組合」元件（由葉節點組成，例如 PricingSection）？
3. 哪些元件會在多個地方重複使用（值得抽取成共用元件）？

用樹狀格式表示：
```
LandingPage
├── Navbar
│   ├── Logo
│   ├── NavLinks
│   └── CTAButton（共用）
├── HeroSection
│   ├── Headline
│   ├── Subheadline
│   └── CTAButton（共用）
└── ...
```

### 任務 2：Server vs Client 決策
對每個主要元件，決定：Server Component 還是 Client Component？

判斷原則：
- 需要 useState / useEffect → Client Component
- 有互動（按鈕點擊、表單輸入） → Client Component
- 靜態展示 / 無互動 → Server Component（預設）

| 元件 | 類型 | 理由 |
|------|------|------|
| Navbar | Client | 需要 mobile menu 的 useState |
| HeroSection | Server | 靜態內容，無互動 |
| ... | ... | ... |

## 完成後
將元件樹 + Server/Client 決策表存入 `answer/ex01-answer.md`
