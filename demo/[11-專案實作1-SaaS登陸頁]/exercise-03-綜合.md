# 練習 03 — 綜合挑戰：完整登陸頁 + 部署

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
用 Claude Code 完成完整的 SaaS 登陸頁，並部署到 Vercel。

## 要求

1. **整合所有元件**
   將以下元件組合成完整的單頁應用：
   - Navbar（含 Logo + 導覽連結 + CTA）
   - Hero Section（來自練習 02）
   - Features Section（3-4 個功能特色，每個有 icon + 標題 + 說明）
   - Pricing Table（來自練習 02）
   - CTA Section（最後行動呼籲，和 Hero 有所不同）
   - Footer（連結 + 版權聲明）

2. **加入 Dark Mode**
   使用 Tailwind CSS 的 `dark:` 前綴：
   - 背景：深色模式下換成深灰色
   - 文字：深色模式下換成白色/淺灰色
   - 使用 localStorage 記憶使用者偏好

3. **截圖驗證（Puppeteer 或手動）**
   在以下三個寬度截圖並存入 `answer/screenshots/`：
   - 375px（iPhone SE）
   - 768px（iPad）
   - 1280px（桌面）
   
   各提供 light mode 和 dark mode，共 6 張截圖。

4. **部署到 Vercel**
   完成部署並提供線上連結，驗證：
   - 所有元件在 production 環境正常顯示
   - Dark mode 切換功能正常
   - 行動版 Navbar 的展開/收合功能正常

## 完成標準
- [ ] 6 個主要元件全部實作
- [ ] Dark mode 正常運作
- [ ] 6 張截圖存入 answer/screenshots/
- [ ] Vercel 連結可以訪問

## 完成後
將 Vercel 連結 + 截圖存入 `answer/ex03-answer.md`
