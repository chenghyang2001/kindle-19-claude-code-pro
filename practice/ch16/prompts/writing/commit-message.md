# Commit Message 撰寫

## 用途
改完程式要 commit，讓 Claude 依 diff 產出符合團隊格式的 commit message。

## 變數
| 變數 | 說明 | 範例 |
| --- | --- | --- |
| `{{convention}}` | 團隊 commit 格式 | 繁體中文「動詞 + 簡短說明」 |
| `{{diff}}` | `git diff --staged` 輸出 | （貼上 diff） |

## 模板
---
請依照下面的 diff 寫一則 commit message。

格式規範：{{convention}}
規則：
1. 第一行 50 字以內，說明「做了什麼」。
2. 空一行後用條列說明「為什麼」與重要細節，最多 5 點。
3. 不要描述 diff 裡沒有的改動。

diff：
```
{{diff}}
```

輸出格式：只輸出 commit message 本身，放在一個程式碼區塊內。
---

## 範例填入
- convention = `繁體中文，動詞開頭（新增/修復/重構/更新/移除）`
- diff = `average_price` 加入空清單檢查的 diff

## 預期輸出格式
```
修復 average_price 空清單除以零

- 空清單改回傳 0，避免 ZeroDivisionError
```

## 使用說明
可直接用 `git diff --staged | claude -p "$(python tools/fill_prompt.py ...)"` 串起來。

## 版本紀錄
- v1（2026-10-18）初版
