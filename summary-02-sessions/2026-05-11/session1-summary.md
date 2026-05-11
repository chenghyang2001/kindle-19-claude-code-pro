# Session 1 — 2026-05-11

## 完成事項

### 1. 多語言資料夾結構重組
- 原 4 個 Markdown 檔（README.md、appendix-a/b/c）全部移入 `english/` 子資料夾
- 建立繁體中文翻譯版本，存入 `中文/` 子資料夾
- 共 8 個 Markdown 檔（4 英 + 4 中）完整建立

### 2. NotebookLM PPTX 批次下載
- 從 NotebookLM notebook `70cf5579-c61f-445b-9708-00d0b45384d0` 下載全部 18 個 slide deck 投影片（`第01章` 至 `第15章` + `附錄A/B/C`）
- 儲存至 `pptx/` 子資料夾
- 刪除所有含 `(2)` 的重複檔案及垃圾 `pptx${NAME}*.pptx` 檔

### 3. PPTX → PNG 批次轉換（pymupdf）
- PowerPoint COM 自動化因 MOTW（Mark of the Web / Protected View）全部失敗
- 改用 `pymupdf` (fitz v1.27.2.2) 直接讀 PPTX，無需 COM 或外部程式
- 18 個 PPTX → 266 張 PNG（150 DPI），輸出至 `pptx/png/`

### 4. 投影片瀏覽器 HTML 生成（gen_viewer.py）
- 建立 `gen_viewer.py`：掃描 `pptx/png/*.png` → 生成 `pptx/index.html`
- Sidebar 版型：左側 200px 章節導覽（18 個章節按鈕）+ 主圖區滾輪縮放/拖曳/平移 + 底部縮圖列
- IMAGES 陣列 266 筆、CHAPTERS 陣列 18 項、CHAPTER_START 索引 map
- SHA256: `51710789b621d82ca0914f0bc487554810cd32e0e81a570b5ae161c50fd574ac`

### 5. GitHub Pages 部署（claude-code-pro-pptx）
- 建立 GitHub repo `chenghyang2001/claude-code-pro-pptx`（public）
- 推送 268 個檔案（1 index.html + 1 .nojekyll + 266 PNG）
- 啟用 GitHub Pages，輪詢等待 `status=built`（54 秒）
- 部署 URL：https://chenghyang2001.github.io/claude-code-pro-pptx/

### 6. mermaid-viewer 統一入口更新
- 在 `chenghyang2001/mermaid-viewer` 的 `index.html` 新增第 8 個 tab：「Claude Code Pro（266 張）」
- 插入 CSS rule（`active-claude-code-pro-pptx`）、tab button（data-idx=7）、pane iframe、ACTIVE_CLASS 陣列更新
- commit `7634f60`，Pages rebuild 完成

### 7. 自動播放功能新增
- 在 `pptx/index.html` nav bar 新增 `▶ 自動播放 ▼` split-button
- 主按鈕：播放/暫停切換（▶ / ⏸）；下拉選單：3/5/10/15 秒速度選擇
- 播放中按鈕變藍色（`#0ea5e9`），按 Escape 停止
- 同步推送到 `claude-code-pro-pptx` GitHub Pages repo，commit `429393a`

## 關鍵技術筆記

### pymupdf 開 PPTX 無需 COM
- `fitz.open("file.pptx")` 在 pymupdf ≥ 1.24 直接支援，不需要 Office 安裝
- Windows MOTW（Mark of the Web）會讓 PowerPoint COM（comtypes/win32com）的所有 PPTX 開啟失敗（E_FAIL），即使用 `Unblock-File` 移除 zone 標記仍無效
- Claude Code session 缺少互動式桌面 context，COM automation 本質上不可靠

### Git 路徑雙根問題
- Git Bash 的 `/c/Users/B00332/temp-xxx` 路徑實際對應 Windows `C:\c\Users\B00332\temp-xxx`（有雙重 `C:\c\` 前綴）
- `ls` 看不到但 `git -C /c/...` 可以運作
- 解法：用 Python `os.listdir('/c/Users/B00332/...')` 直接操作，避免路徑解析歧義

### Puppeteer Pages 驗證模式
- `mcp__puppeteer__puppeteer_navigate` 有時 timeout，需先 navigate 再 screenshot（兩個 call 分開，而非一次嘗試）
- 第一次 navigate 失敗後再試一次，通常第二次成功；也可直接 screenshot（browser 記住上次 URL）

### mermaid-viewer 插入錨點
- CSS 錨點：`    /* ── Panes ── */`（含 4 個空格前綴）
- Tab button 錨點：最後一個 `</button>` 後接 `</div>` 的位置
- Pane 錨點：第一個 `<script>` 標籤前

## 產出檔案表格

| 路徑 | 說明 |
|------|------|
| `english/README.md` | 英文原版 README |
| `english/appendix-a-prompt-library.md` | 英文附錄 A |
| `english/appendix-b-team-claude-md.md` | 英文附錄 B |
| `english/appendix-c-security-checklist.md` | 英文附錄 C |
| `中文/README.md` | 繁體中文 README |
| `中文/appendix-a-prompt-library.md` | 繁體中文附錄 A |
| `中文/appendix-b-team-claude-md.md` | 繁體中文附錄 B |
| `中文/appendix-c-security-checklist.md` | 繁體中文附錄 C |
| `gen_viewer.py` | PPTX/PNG → HTML 瀏覽器生成腳本 |
| `pptx/index.html` | 投影片瀏覽器（266 張，含自動播放） |
| `pptx/*.pptx` | 18 個 PPTX 檔（第01章-第15章 + 附錄A/B/C） |
| `pptx/png/*.png` | 266 張 PNG 投影片圖片 |
| GitHub: `chenghyang2001/claude-code-pro-pptx` | 部署 repo（266 PNG + index.html）|

## HANDOFF（下次 session 優先處理）

### 立即行動
- [ ] 考慮更新 `gen_viewer.py` 以在重新生成時自動包含自動播放按鈕（目前 HTML 是手動加的，若重跑 gen_viewer.py 會蓋掉自動播放功能）
- [ ] 若有需要可為 `pptx/index.html` 的 mermaid-viewer badge 更新正確數量（目前 mermaid-viewer 顯示 266 張正確）
- [ ] 確認 `pptx/` 資料夾中 PPTX 下載完整性（18 章節均已下載）

### 進行中（需接續）
- `gen_viewer.py` 尚未更新以涵蓋自動播放功能；手動加入 HTML 的自動播放在未來若重新生成 index.html 時會遺失
- GitHub Pages repo `claude-code-pro-pptx` 已部署，mermaid-viewer 已整合，無未完成工作

### 注意事項
- Windows MOTW 問題：直接從 NotebookLM 下載的 PPTX 無法用 COM automation 開啟，必須用 pymupdf
- Git Bash 路徑雙根：`/c/Users/...` 在 git clone 時會在 `C:\c\Users\...` 建立目錄，與 Python 的 `C:\Users\...` 不同路徑空間
- mermaid-viewer 插入時要先 `git pull --rebase` 再插入（遠端可能已有新 commit），避免衝突
- Puppeteer 對 GitHub Pages 的 navigate 常 timeout（30s），建議先 navigate（允許失敗）再 screenshot（用上次 cache）
