# Session 14 Summary — 2026-06-17

## 完成事項

### 提示詞庫深度解析（兩個資料夾的關係）

- 解釋了 `提示詞-150-files-演練/` 與 `提示詞-150-files-範本/` 的關係：
  - **範本版**：含 `[佔位符]` 語法，使用者複製後填入自己的資訊
  - **演練版**：同一份模板但佔位符已填入真實示例，讓使用者先看「填好的樣子」再填自己的
  - 兩者一一對應，相同的 A–N 分類 × 150 個檔案
- 解析了 14 個分類（A 核心框架 / B 功能開發 / C 除錯與診斷 ... N 效能優化）
- 說明「不是每次用 10 個模板，而是依當前任務選最相關的 1-2 個」

### 建立 prompt-pick Skill

- **需求**：使用者不想記憶任何 ID 或名稱，希望透過選單導引
- **設計**：兩層選單 — Level 1 顯示 A–N 分類 → 使用者輸入字母 → Level 2 Bash 動態列出該分類所有檔案 → 使用者輸入數字 → 同時顯示演練示範 + 範本 + 佔位符清單
- **技術決策**：Level 2 用 `ls` 動態讀取（新增模板自動出現在選單，無需修改 SKILL.md）
- **SKILL.md 位置**：`~/.claude/skills/prompt-pick/SKILL.md`
- **觸發詞**：`pp`, `選模板`, `找提示詞`, `提示詞庫`, `prompt-pick`, `選提示詞`, `pick prompt`

## 產出檔案

| 檔案 | 說明 |
|------|------|
| `~/.claude/skills/prompt-pick/SKILL.md` | 150 提示詞模板兩層選單 Skill（新建） |
| `memory/MEMORY.md` | 新增 Session 10 Skill 記錄（更新） |

## 關鍵技術筆記

### Skill 設計模式：靜態 + 動態兩層選單

- Level 1 靜態（14 分類固定），可在選單旁加情境說明（← 東西跑很慢不知哪裡慢）
- Level 2 用 Bash `ls` 動態，保持與檔案系統同步，不需維護硬編碼清單

### 兩個提示詞資料夾的最佳使用流程

1. 先看「演練版」了解填好是什麼樣子
2. 再複製「範本版」，依佔位符清單逐一填入
3. 貼給 Claude 執行

### 佔位符設計哲學

- `[xxx]` 格式讓使用者「先盤點材料再送出」
- 避免「貼出去才發現少了 stack trace」的情況
- `[A / B / C]` 這類斜線格式代表「擇一選項」，也算佔位符

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 試用 `/pp` skill — 觸發後應顯示 A–N 選單，選 C（除錯）→ 選數字 → 確認演練+範本+佔位符三區塊都正確顯示
- [ ] 開始 Lesson 11（專案實作 1 — SaaS 登陸頁），starter/ 已含 Lesson 10 的 answer

### 進行中（需接續）

- Lesson 11 starter/ 已就緒（carry 從 Lesson 10 answer 攜帶），可直接開始練習
- `freelancer-dashboard/` 第 13 章演練環境已設定（db:push/seed/dev 可跑），尚未完成課程

### 注意事項

- `prompt-pick` skill 路徑含中文（14 個目錄名都有中文），Bash ls 命令要用雙引號包住路徑
- 本 session 沒有 git commit（只建了 ~/.claude/ 底下的 skill 檔案，沒有改動 project repo）
- Lesson 10 的 answer + EPUB + carry 已在前幾個 session 完成（commit 2b1fce4）
