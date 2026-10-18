# 練習 01 — 基礎：從快樂路徑到生產級

## 情境說明
你接手一個「只處理正常情況」的程式碼，需要讓它達到生產標準。

## 任務

### 任務 1：識別缺陷
審查以下函式，列出所有安全與品質問題：

```python
def fetch_user(user_id):
    conn = pymysql.connect(host='localhost', db='app',
                           user='root', password='1234')
    result = conn.execute(f"SELECT * FROM users WHERE id={user_id}")
    return result.fetchone()
```

需識別的問題類型：
- SQL 注入風險
- 硬編碼機密
- 連線資源洩漏
- 缺少錯誤處理
- 回傳值不確定性

### 任務 2：重寫為生產級
用 Claude Code 重寫這個函式，要求：
1. 參數化查詢（防 SQL 注入）
2. 連線字串從環境變數讀取
3. 用 try/finally 確保連線關閉
4. 明確的回傳型別（找到回傳 dict，找不到回傳 None）
5. 適當的錯誤 logging

## 完成後
將原始問題清單 + 修正後的程式碼存入 `answer/ex01-answer.md`
