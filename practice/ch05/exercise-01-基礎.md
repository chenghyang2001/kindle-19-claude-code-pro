# 練習 01 — 基礎：Stack Trace 解讀

## 情境說明
你的同事留下了一個有 bug 的 Python 腳本，只留了一個 stack trace，沒有任何說明。

## 任務

### 任務 1：解讀錯誤
給定以下 stack trace，分析：

```
Traceback (most recent call last):
  File "main.py", line 23, in <module>
    result = process_data(df)
  File "processor.py", line 45, in process_data
    return df["timestamp"].apply(parse_date)
  File "processor.py", line 12, in parse_date
    return datetime.strptime(s, "%Y-%m-%d")
ValueError: time data "2024/01/15" does not match format "%Y-%m-%d"
```

回答以下問題：
1. 錯誤類型是什麼？
2. 錯誤發生在哪個檔案的第幾行？
3. 根本原因是什麼（不是症狀，是真正的原因）？
4. 資料來源可能是什麼（日期格式 2024/01/15 暗示了什麼）？

### 任務 2：寫修復程式碼
根據分析，寫一個能處理多種日期格式的 `parse_date` 函式：
- `YYYY-MM-DD`（原本支援的）
- `YYYY/MM/DD`（新發現的）
- `DD-MM-YYYY`（預防性支援）
- 遇到無法解析的格式時回傳 None 並 log 警告

## 完成後
將分析結果 + 修復程式碼存入 `answer/ex01-answer.md`
