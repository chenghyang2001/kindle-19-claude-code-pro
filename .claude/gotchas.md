# 踩坑記錄（Gotchas）

> AI 自動更新。每次練習遇到非預期問題時，告訴 Claude「記到 gotchas.md」。
> 目的：下次同類問題，AI 直接引用此處解法，不重蹈覆轍。

---

## 工具層面踩坑

### [2026-06-16] Read 工具無法讀取 .pptx 二進位檔案

**症狀**：`Read` 工具在讀取 `.pptx` 檔案時報錯 `This tool cannot read binary files`。
**根本原因**：`.pptx` 是 ZIP 壓縮的二進位格式，Read 工具只處理文字。
**解法**：改用 Python `zipfile` 模組解壓縮，再讀取 `ppt/media/image*.png` 圖片。
**應用場景**：任何需要解析 Office 格式（.pptx/.docx/.xlsx）的任務。

### [2026-06-16] 第03章 pptx 內容全是圖片，無法用 XML 解析文字

**症狀**：Python zipfile 解壓後搜尋 `<a:t>` XML 標籤，每張投影片返回 0 個文字節點。
**根本原因**：投影片是「截圖放大」設計，實際內容以 PNG 圖片嵌入（`<p:pic>` 元素）。
**解法**：改用 Vision 能力直接 Read `.png` 圖片，視覺解讀文字內容。
**應用場景**：遇到任何 Office 文件顯示「空白 XML」時，先查 `ppt/media/` 確認是否全為圖片。

### [2026-06-16] Python 腳本在 Git Bash 中的路徑問題

**症狀**：在 Git Bash 中執行 `cd chapter-pptx && python3 script.py`，腳本內相對路徑計算錯誤。
**根本原因**：Bash tool 的 `cd` 在子 shell 中執行，不保留到下一次 Bash 呼叫。
**解法**：腳本中使用 `os.path.expanduser('~') + '/workspace/...'` 絕對路徑，不依賴工作目錄。

---

## 概念層面踩坑

### [Lesson 03] Hook command 太複雜時難以維護

**症狀**：在 settings.json 的 `command` 欄位寫複雜邏輯（多個 pipe + json 解析），導致 JSON 轉義地獄。
**根本原因**：JSON 字串中的引號需要多層轉義，讀起來幾乎不可維護。
**解法**：複雜邏輯外移到 `~/.claude/hooks/script.py`，settings.json 的 command 只調用腳本。
**應用場景**：任何 Hook command 超過一行時，立刻外移為獨立腳本。

### [Lesson 02] Output Style 的英文指示不可凌駕語言鐵律

**症狀**：session 被設為 explanatory/learning output style（英文），回覆飄移成英文。
**根本原因**：output style 的英文指示被誤解為要改用英文回覆。
**解法**：CLAUDE.md 語言鐵律（繁體中文）凌駕 output style 指示，始終維持繁中。
