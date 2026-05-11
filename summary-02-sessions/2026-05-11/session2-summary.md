# Session 2 — 2026-05-11

## 完成事項

### 1. Phase 4 Puppeteer 截圖驗證（接續上次 session）
- 上次 session 遺留的 Puppeteer navigate timeout 問題：本次改為先 navigate（允許失敗）再直接 screenshot，成功截圖確認 `https://chenghyang2001.github.io/claude-code-pro-pptx/` 正常載入
- 截圖顯示 266 張投影片、18 章節側欄、底部縮圖列均正常顯示

### 2. Phase 5 mermaid-viewer 統一入口整合
- 克隆 `chenghyang2001/mermaid-viewer` repo（路徑解析問題：git clone 目的地實際在 `C:\c\Users\B00332\temp-mermaid-viewer-update`，需用 `git -C /c/...` 操作）
- 遠端已有新 commit（7 → 8 tabs），reset to origin/main 後重新插入第 8 tab（index=7）
- 插入四處：CSS rule、tab button（data-idx=7）、pane iframe（data-src）、ACTIVE_CLASS 陣列
- commit `7634f60`，Pages rebuild 完成，mermaid-viewer 顯示「Claude Code Pro」tab

### 3. 自動播放按鈕新增（pptx/index.html）
- 使用者指出瀏覽器缺少「自動播放」功能，直接編輯 `pptx/index.html`（.html 不在 writer-qa 鐵律清單）
- 新增 `▶ 自動播放 ▼` split-button：主按鈕切換播放/暫停、dropdown 選速度（3/5/10/15 秒）
- 播放中按鈕底色轉藍（`#0ea5e9`），Escape 鍵停止
- commit `f5b1e1d`，同步推送 `claude-code-pro-pptx` Pages repo（commit `429393a`）

### 4. gen_viewer.py 模板更新（writer-qa 鐵律流程）
- 使用者要求將自動播放功能納入 `gen_viewer.py` 的 `HTML_TEMPLATE`，避免重新生成時遺失
- 複雜度評估 medium（單檔，~40 行插入）→ 走 code-writer → code-qa（不加 reviewer）
- code-writer 完成：SHA256 `843c5afccbdf87553a0b88ef609e1725cbbc0e0cfe2e57b77950af7e5ea8a26d`，300 行
- code-qa 全 PASS（V1~V5，ruff 0 warning）：生成的 index.html 38692 bytes，三個關鍵字串均存在
- commit `7d03c52`

### 5. GitHub Pages 最終同步
- QA 執行 gen_viewer.py 時已重生成 `pptx/index.html`（HTML entity 版本 &#9658;/&#9660;）
- 克隆 `claude-code-pro-pptx` Pages repo，複製新 index.html，commit `c528032`
- Pages rebuild 完成，https://chenghyang2001.github.io/claude-code-pro-pptx/ 現為 gen_viewer.py 原生版本

## 關鍵技術筆記

### Puppeteer GitHub Pages 驗證技巧
- navigate 常 timeout（30s），因為 Pages 載入 266 張縮圖慢
- 解法：先 navigate（接受 timeout），再直接呼叫 screenshot — browser 記住上次 URL，screenshot 從 cache 取，通常成功

### mermaid-viewer Git 路徑雙根陷阱（再次踩到）
- `git clone /c/Users/...` 在 Bash 下實際建立 `C:\c\Users\...`（`/c/` 被解析為 C 磁碟下的 `c` 子目錄）
- `ls` 看不到但 `git -C /c/...` 可以操作（git 用 Win32 API 直接存取）
- 跨 session 解法：改用 Python `subprocess` + Windows 絕對路徑（`r'C:\...'`）做所有 git 操作

### writer-qa 鐵律在 HTML 模板修改的適用邊界
- `HTML_TEMPLATE` 是 Python `.py` 檔內的字串，修改它屬於修改 `.py` 檔 → 觸發鐵律
- 反之直接修改已生成的 `.html` 不觸發鐵律（.html 不在清單）
- 兩者效果等同，但 `.py` 改動是持久的（不會被重生成覆蓋）

### HTML Entity vs Unicode 在 Python 字串中
- Python 多行字串直接寫 `▶` `⏸` 是合法 UTF-8，但 JS 的 textContent 賦值需要用 Unicode escape 或直接字元
- writer 選擇 HTML button 用 entity（`&#9658;`），JS 字串直接用 Unicode 字元，兩者皆可
- 關鍵：`HTML_TEMPLATE` 中的 `\n` 不會被 JS 誤解，因為它在字串字面量內

## 產出檔案表格

| 路徑 | 說明 | commit |
|------|------|--------|
| `pptx/index.html` | 自動播放版本（gen_viewer.py 重生成） | `7d03c52` |
| `gen_viewer.py` | HTML_TEMPLATE 內建自動播放按鈕 | `7d03c52` |
| GitHub: `chenghyang2001/claude-code-pro-pptx` index.html | Pages 同步更新 | `c528032` |
| GitHub: `chenghyang2001/mermaid-viewer` index.html | 新增 Claude Code Pro tab | `7634f60` |

## HANDOFF（下次 session 優先處理）

### 立即行動
- [ ] 目前 `gen_viewer.py` 的 `HTML_TEMPLATE` 標題寫死為「Claude Code Pro — 投影片瀏覽器」，若未來要用於其他書籍 PPTX，需將標題參數化（加 `__TITLE__` 佔位字串）

### 進行中（需接續）
- 所有 deploy-viewer 工作已完成，無待處理項目
- `pptx/` 資料夾的 PPTX/PNG/HTML 已全部同步至 GitHub Pages

### 注意事項
- mermaid-viewer tab 操作：遠端 repo 變化頻繁，每次操作前必須先 `git pull` / `reset to origin/main`，否則推送會衝突
- `git clone` 路徑雙根問題持續存在（見技術筆記），建議所有 temp clone 改用 Python subprocess + Windows 路徑
- Puppeteer screenshot 對 GitHub Pages 的穩定做法：navigate（允許 timeout）→ screenshot（不 await navigate）
