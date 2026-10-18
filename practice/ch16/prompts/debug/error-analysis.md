# 除錯助手：錯誤訊息分析

## 用途
程式丟出 exception 或錯誤訊息、自己一時看不出原因時，讓 Claude 從錯誤訊息推根因並給解法。

## 變數
| 變數 | 說明 | 範例 |
| --- | --- | --- |
| `{{error_message}}` | 完整錯誤訊息（含 traceback） | ZeroDivisionError: division by zero |
| `{{code}}` | 出錯的相關程式碼 | （貼上函式） |
| `{{input}}` | 觸發錯誤的輸入值 | items = [] |
| `{{environment}}` | 執行環境 | Python 3.12 / Windows 10 |
| `{{tried}}` | 已經試過的方法（沒有就寫「無」） | 無 |

## 模板
---
你是一位擅長系統性除錯的工程師。請用「假設 → 驗證」的方式分析以下錯誤。

錯誤訊息：
```
{{error_message}}
```

相關程式碼：
```
{{code}}
```

觸發輸入：{{input}}
環境：{{environment}}
已試過：{{tried}}

請依序回答：
1. 根本原因（一句話）。
2. 為什麼這個輸入會觸發它（對應到哪一行）。
3. 修正方式（附程式碼），以及修正後該輸入的預期行為。
4. 一個可以防止回歸的測試案例。
不要猜測沒有證據的原因；資訊不足時列出你需要的額外資訊。
---

## 範例填入
- error_message = `ZeroDivisionError: division by zero`（`average_price([])` 的 traceback）
- code = `samples/order_utils.py` 的 `average_price`
- input = `items = []`
- environment = `Python 3.12 / Windows 10`
- tried = `無`

## 預期輸出格式
四個編號段落：根因 / 觸發路徑 / 修正碼 / 回歸測試。

## 使用說明
一定要貼「完整」traceback，不要只貼最後一行；`tried` 可以避免 Claude 重複建議你已經試過的方法。

## 版本紀錄
- v1（2026-10-18）初版
