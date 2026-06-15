# 練習 03 — 綜合挑戰：建立 Debug 工具箱

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
建立一套個人化的 Claude Code debug 工具箱，讓未來遇到 bug 時可以快速啟動。

## 要求

1. **設計 3 個 Debug 提示詞模板**

   分別適用於：
   - **語法錯誤**（SyntaxError / TypeError 等）：提示詞讓 Claude Code 快速定位並修復
   - **邏輯錯誤**（程式跑起來但結果不對）：提示詞讓 Claude Code 系統性地驗證每個邏輯分支
   - **效能問題**（程式太慢）：提示詞讓 Claude Code 分析瓶頸並提出優化方案

   每個模板格式：
   - 名稱
   - 使用時機
   - 完整提示詞（含角色設定 + 分析步驟 + 輸出格式）

2. **建立 debug-info.md 模板**
   每次 debug 時填寫，讓 Claude Code 快速了解問題情境：
   - 問題描述（一句話）
   - 期望行為
   - 實際行為
   - 已嘗試的方向
   - 相關程式碼（貼哪段？多少行合適？）
   - 環境資訊（Python 版本 / OS / 相依套件）

3. **加入 CLAUDE.md**
   在 CLAUDE.md 中加入「Debug SOP」章節，定義：
   - 遇到不同類型的 bug 時，叫 Claude Code 扮演什麼角色
   - 要求 Claude Code 先列假設清單再行動

## 完成標準
- [ ] 3 個完整的 debug 提示詞模板
- [ ] debug-info.md 模板可以在真實情境中使用
- [ ] CLAUDE.md 的 Debug SOP 章節完成

## 完成後
將解答存入 `answer/ex03-answer.md`
