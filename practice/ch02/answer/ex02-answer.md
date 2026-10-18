# 練習 02 解答 — 設計角色提示詞

> 實驗環境：Claude Code 2.1.302、`claude -p --tools ""`、timeout 120 秒、2026-10-18 實跑。
> 測試情境：**B（TypeScript Code Review）**。原始輸出：`outputs/ex02-b-norole.md`、`outputs/ex02-b-role.md`。

## 任務 1：三種角色設計

設計原則：角色不只是一句「你是專家」，而是 **身分 + 價值觀（在意什麼）+ 方法（檢查順序）+ 輸出格式**。

### 情境 A：除錯 Python 爬蟲（Scrapy）

```text
你是有 8 年經驗的資深 Python 爬蟲工程師，熟悉 Scrapy 的 request 排程、middleware 與 selector。
你的除錯原則是「先重現、再假設、最後驗證」，不在沒有證據時直接改 code。

請依以下順序系統性檢查下方爬蟲：
1. 流程控制：callback、分頁終止條件、yield 的 Request 是否可能是 None 或相對路徑
2. 資料擷取：CSS/XPath 選擇器在元素缺失時的行為（.get() vs .extract()[0]）
3. 防護與禮貌：robots.txt、DOWNLOAD_DELAY、User-Agent、重試與 HTTP 錯誤碼
4. 輸出：item 欄位缺值、編碼（UTF-8）

輸出格式：
- 問題表格：| 編號 | 位置 | 症狀（會看到什麼 log / 例外） | 根因 | 嚴重度 |
- 每個問題附「如何用 scrapy shell 或 log 驗證」的一行指令
- 修正後完整程式碼
- 不確定的地方請標明「假設」，不要編造 Scrapy 不存在的 API

（範例程式碼：samples/quotes_spider.py）
```

> 範例爬蟲埋了兩個典型 bug：最後一頁 `next_page` 為 `None` 時仍 `yield scrapy.Request(None)`（拋 `TypeError`）且沒用 `response.follow` 處理相對路徑；`.extract()[0]` 在缺作者時 `IndexError`。本機未安裝 Scrapy，此情境未實跑。

### 情境 B：Code Review TypeScript（本次實測的角色）

```text
你是一位極度嚴格的 TypeScript 型別安全專家（strict mode 信徒，視 `any` 為禁字），正在做 PR Code Review。

審查重點（依序檢查）：
1. `any`、型別斷言 `as`、非空斷言 `!` 是否在掩蓋真正的型別錯誤
2. 外部資料邊界（fetch / JSON.parse）是否有 runtime 驗證，還是直接信任
3. 型別斷言是否藏住了邏輯 bug
4. 錯誤處理（HTTP 非 2xx、網路錯誤）

請注意：這段程式碼在 `tsc --strict` 下編譯 0 錯誤，所以請找出「編譯器看不到」的問題。

輸出格式：
- 表格：| 嚴重度(🔴必改/🟡建議) | 位置 | 問題 | 會造成的 runtime 後果 |
- 修正後的完整程式碼（不引入第三方套件，可手寫 type guard）
- 最後一句話總結最大風險
```

### 情境 C：設計 REST API（向後相容與版本管理）

```text
你是負責公開 API 的 API 設計師，服務已有上千個外部整合方，你最怕的事是「改版讓別人的整合壞掉」。

任務：為「訂單系統」新增「部分出貨」功能，現有 v1 的 GET /v1/orders/{id} 回傳 { status: "shipped" | "pending" }。

設計時必須回答：
1. 這個變更是 breaking 還是 non-breaking？依據什麼規則判斷（新增欄位、新增 enum 值、改型別、改語意）
2. 版本策略：URL 版本（/v2）、Header 版本、或不升版用新增欄位？比較三者並選一個
3. 舊客戶端收到新 enum 值（例如 "partially_shipped"）會怎樣？如何降級
4. Deprecation 流程：Sunset / Deprecation header、公告期、監控舊版流量

輸出格式：
- 變更分類表：| 變更 | breaking? | 理由 |
- 選定方案的 OpenAPI 片段（YAML）
- 遷移時程表（T0 / T+3 月 / T+6 月 各做什麼）
- 一段「給外部開發者的變更公告」草稿
```

## 任務 2：測試與比較（情境 B，同一段程式碼）

- **無角色**：`請幫我看一下這段 TypeScript 程式碼有什麼問題。` + 程式碼（`prompts/ex02/b-norole.txt`）
- **有角色**：上方情境 B 角色提示詞 + 同一段程式碼（`prompts/ex02/b-role.txt`）
- 程式碼：`samples/user_service.ts`，刻意埋了 `any` 快取、`as User`、`email!`、`as string` 藏住的大小寫 bug、`JSON.parse` 隱式 any；**`tsc --strict` 下 0 錯誤**（測試證實；拿掉 `as string` 後 tsc 會報 TS2367）

### 量化比較

| 指標 | 無角色 | 有角色 |
| --- | ---: | ---: |
| 耗時 | 69.8 秒 | 87.2 秒 |
| 回答字數 | 4120 | 6980 |
| 找到的問題數 | 9（🔴5 / 🟡4） | 13（🔴8 / 🟡5） |
| 輸出結構 | 標題 + 條列 | 表格（含 runtime 後果欄） |
| 修正版行數 | 64 | 140 |
| 修正版殘留 `!` 非空斷言 | 1 | 0 |
| 修正版 `tsc --strict` | ✅ 通過 | ✅ 通過 |
| 修正版 runtime 測試（6 項） | ✅ 6/6 | ✅ 6/6 |

runtime 測試項目：`isAdmin` 正確、無 email 回 `undefined`、正常 email 取網域、`parseUsers("{}")` 拋錯、陣列內壞資料拋錯、HTTP 404 會 reject **且不被快取**（第二次呼叫仍重抓）。

### 質性比較

| 面向 | 無角色 | 有角色 |
| --- | --- | --- |
| **深度** | 核心 5 個問題全抓到（`isAdmin` 永遠 false、`!` 崩潰、沒查 `res.ok` 且錯誤被永久快取、`as User` 無驗證、`parseUsers`）。另有原型鏈、路徑注入、併發重抓、快取無上限 | 同樣 5 個核心問題 + **只有角色版抓到的**：`split("@")[1]` 對 `a@b@c.com` 取錯值、`fetch` 無 timeout、錯誤無上下文、快取回傳同一物件參考可被竄改、回應 `id` 與請求不一致的檢查 |
| **專業度** | 有給 ESLint 規則、`noUncheckedIndexedAccess`、建議 Zod | 更「型別系統」導向：`satisfies` 綁定 role 聯集、`unknown` 進入邊界、`Object.freeze`、`consistent-type-assertions: never`、`exactOptionalPropertyTypes` |
| **切入點** | 從「哪裡會壞」出發，偏一般 code review（也談安全、效能） | 從「哪個斷言在說謊」出發，每個問題都對應到「編譯器為什麼沒發現」→ 完全照角色的檢查順序 |
| **缺點** | 修正版自己還留了 `!` | 嚴重度偏高（13 個裡 8 個 🔴，原型鏈也列 🔴）；修正版 140 行，比原碼大 4 倍，有過度工程化傾向 |

### 結論

1. **有角色 → 切入點聚焦、覆蓋面更深**：多找到 4 個問題，每個都對到「斷言掩蓋了什麼」。
2. **差距沒有想像中大**：無角色版本就已抓到所有核心 bug。真正拉開差距的是角色裡的**檢查清單 + 「tsc 0 錯誤」的提示 + 表格格式**，而不是「你是專家」這句話本身。
3. **角色會放大它的價值觀**：「極度嚴格」讓嚴重度膨脹、修正版變很長。要在角色裡加上「嚴重度分級標準」與「修正版不超過原碼 2 倍」之類的限制來平衡。

## 延伸思考

### 什麼情況下角色設定沒幫助，甚至讓品質下降？

| 情況 | 為什麼 |
| --- | --- |
| 任務本身很單純（格式轉換、改 typo、查語法） | 角色只增加 token，不增加資訊 |
| 角色只有頭銜沒有方法（「你是世界頂尖專家」） | 模型本來就會盡力，空頭銜不帶來新的檢查視角，有時只換來更浮誇的語氣 |
| 角色與任務衝突或太窄 | 「Python 專家」去看前端 bug，會把問題往自己熟悉的方向拉 |
| 價值觀過度強烈（「極度嚴格」「零容忍」） | 本實驗實證：嚴重度膨脹、修正版過度工程化 |
| 要求創意發散或多元觀點 | 單一角色會收窄視角；應改用多角色或對比提示 |
| 角色暗示了不存在的權威（「你是本公司架構師」） | 模型會「扮演」去猜公司慣例，容易捏造 |
| 已有很完整的 CLAUDE.md／系統規範 | 角色和既有規範重疊，邊際效益很低（本實驗無角色組也吃到全域 CLAUDE.md，差距因此被縮小） |

### 最值得精心設計並保存的角色提示詞

**「型別／資料邊界嚴格的 Code Reviewer」**（即情境 B 的進化版）最值得保存，理由：

- 使用頻率最高：每個 PR、每段 AI 產出的程式碼都要過。
- 本實驗證明它能抓到 `tsc --strict` 抓不到的問題，價值可量化。
- 可以改成可重用的資產：存成 `.claude/agents/strict-reviewer.md` 或 slash command，再補上「嚴重度標準」「修正版長度上限」兩條限制，修掉本次觀察到的過度嚴格問題。

次優先是情境 C 的 **API 相容性設計師**：使用頻率低，但一次失誤（breaking change）的代價很高，值得預先寫好檢查清單。
