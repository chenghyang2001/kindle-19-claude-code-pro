# 練習 03 — 綜合挑戰：設計三代理工作流

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
設計一個完整的「技術趨勢週報生成系統」三代理工作流。

## 系統規格

三個 agent：
- **Agent 1（收集者）**：從 GitHub Trending 收集本週熱門 repo
- **Agent 2（分析者）**：對每個 repo 分析技術亮點和應用場景
- **Agent 3（寫作者）**：整合分析結果，生成 800 字技術趨勢週報

## 要求

1. **定義每個 agent 的 Schema**
   使用 JSON Schema 格式定義每個 agent 的輸入和輸出。

2. **設計 Workflow 腳本架構**
   用偽程式碼（pseudo-code）設計 workflow 腳本：
   
   ```
   phase("收集")
   repos = await agent("從 GitHub Trending 收集...")
   
   phase("分析")
   analyses = await pipeline(
     repos.items,
     item => agent("分析 repo: " + item.name, ...)
   )
   
   phase("寫作")
   report = await agent("生成週報...", 輸入 = analyses)
   ```

3. **設計錯誤恢復**
   如果某個 repo 分析失敗：
   - 跳過該 repo 繼續分析其他的
   - 還是整個 workflow 停止？
   
   說明你的選擇理由。

4. **效能估算**
   假設：
   - 收集 10 個 repo → 10 秒
   - 分析每個 repo → 20 秒
   - 寫作 → 30 秒
   
   計算：全依序 vs pipeline 並行的總時間

## 完成標準
- [ ] 三個 agent 的 schema 設計完整
- [ ] Workflow 腳本架構清楚（偽程式碼）
- [ ] 錯誤恢復策略有理由支撐
- [ ] 效能估算正確

## 完成後
將解答存入 `answer/ex03-answer.md`
