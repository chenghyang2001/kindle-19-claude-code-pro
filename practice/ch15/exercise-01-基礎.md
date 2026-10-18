# 練習 01 — 基礎：常見安全漏洞偵測

## 情境說明
以下是一段有安全問題的程式碼片段（Node.js + SQL）。你要用 Claude 輔助找出問題。

```javascript
// users.js — 有安全問題的範例（勿直接使用）
app.get('/user', (req, res) => {
  const userId = req.query.id;
  const query = `SELECT * FROM users WHERE id = ${userId}`;
  db.query(query, (err, result) => {
    res.json(result);
  });
});

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username && u.password === password);
  if (user) {
    res.json({ token: jwt.sign({ id: user.id }, 'my-secret-key') });
  }
});
```

## 任務

### 任務 1：識別漏洞
不用 Claude，自己先識別這段程式碼的安全問題：
- 至少找出 3 個安全問題
- 說明每個問題的威脅類型（SQL Injection / 明文密碼 / 等）
- 說明攻擊者可以如何利用這個漏洞

### 任務 2：設計安全審查 Prompt
設計一個 Prompt，讓 Claude 審查程式碼的安全性：
- Prompt 要引導 Claude 按照 OWASP Top 10 逐項檢查
- 要求 Claude 給出具體的漏洞位置（行號）和修復建議
- 要求 Claude 評估每個漏洞的嚴重程度（Critical / High / Medium / Low）

實際執行這個 Prompt，記錄 Claude 找到了哪些問題、有哪些是你沒想到的。

### 任務 3：修復程式碼
根據識別的問題，設計修復後的版本：
- SQL Injection 修復方式
- 密碼安全性修復方式
- JWT 密鑰安全性修復方式

## 完成後
將漏洞分析 + Prompt 設計 + 修復方案存入 `answer/ex01-answer.md`
