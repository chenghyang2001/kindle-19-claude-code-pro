# 練習 02 — 進階：系統化 Debug 流程

## 情境說明
你的 Flask API 在某些條件下回傳 500，但 log 只有「Internal Server Error」，沒有詳細訊息。

## 任務

### 任務 1：建立 Debug Checklist
設計一個「API 回傳 500」的系統化 debug checklist，至少 8 個步驟。

排序原則：從「最可能」到「最不可能」，同時考慮「最快驗證」的順序。

格式：
1. 步驟描述（用主動動詞開頭）
2. 如何執行這個步驟（具體指令或操作）
3. 如果這步有發現 → 下一步做什麼

### 任務 2：加強 Logging
寫一個 Python decorator，可以套在任何 Flask route 上，自動記錄：
- 請求方法 + 路徑 + 參數
- 回應時間（毫秒）
- 回應狀態碼
- 如果拋出 exception：完整的 traceback

使用方式範例：
```
@app.route("/api/users")
@log_request  # 套上 decorator 就自動 logging
def get_users():
    ...
```

## 延伸思考
思考：如果這個 API 每分鐘被呼叫 10,000 次，logging 每個請求會有什麼問題？你會怎麼設計採樣機制？

## 完成後
將解答存入 `answer/ex02-answer.md`
