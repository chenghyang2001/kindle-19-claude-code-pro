# EPUB 輸出目錄

## 製作規則（Google Play Books 相容）

| 規則 | 說明 |
|------|------|
| 副檔名 | `.xhtml`（不是 `.html`） |
| DOCTYPE | XHTML 1.1（不是 HTML5） |
| 禁止 | `<meta charset>` 標籤 |
| mimetype | 剛好 20 bytes，無 `\n`，ZIP_STORED，第一個 |
| 格式版本 | EPUB 2（不用 EPUB 3） |
| 打包工具 | Python `zipfile`（不用 ebooklib） |

## 製作流程

```bash
# 1. 建立 build/ 目錄結構（見下方）
# 2. 寫內容到 build/OEBPS/chapterNN.xhtml
# 3. 執行打包
PYTHONUTF8=1 python epub/build.py <lesson-number>
```

## 已產出

| 課次 | 檔案 | 日期 |
|------|------|------|
| Lesson 01 | lesson-01-claude-code-pro.epub | 2026-06-17 |
