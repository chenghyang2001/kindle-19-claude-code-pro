# 寫測試

## 用途
寫完一個函式、或要修 bug 前，讓 Claude 產出涵蓋正常 / 邊界 / 錯誤三類的測試案例。

## 變數
| 變數 | 說明 | 範例 |
| --- | --- | --- |
| `{{framework}}` | 測試框架 | pytest |
| `{{function_code}}` | 要測的函式 | （貼上函式） |
| `{{module_path}}` | import 路徑 | order_utils |
| `{{behaviors}}` | 你期望的行為（規格） | 折扣 0~100、空清單回 0 |

## 模板
---
你是一位重視測試品質的工程師。請用 {{framework}} 為下面的函式寫測試。

函式（從 `{{module_path}}` import）：
```
{{function_code}}
```

期望行為：{{behaviors}}

要求：
1. 至少包含三類案例：正常案例、邊界案例（空值 / 0 / 極大值）、錯誤案例（非法輸入應拋錯）。
2. 每個測試函式名稱要說明它驗證什麼，例如 test_discount_zero_returns_full_price。
3. 不要 mock 不必要的東西；不要連網路。
4. 如果期望行為和目前實作衝突，在測試上方用註解標出「此測試預期會失敗，因為…」。

輸出格式：一個完整可執行的測試檔（單一程式碼區塊），之後用條列說明每個案例覆蓋的情境。
---

## 範例填入
- framework = `pytest`
- function_code = `samples/order_utils.py` 的 `calc_total`
- module_path = `order_utils`
- behaviors = `discount 為 0~100 的百分比；空清單回 0；結果四捨五入到小數 2 位`

## 預期輸出格式
一個 `test_order_utils.py` 程式碼區塊 + 條列說明。

## 使用說明
`behaviors` 是重點：沒有寫規格，Claude 只會照現有實作寫測試，抓不到 bug。

## 版本紀錄
- v1（2026-10-18）初版
