# 練習 01 解答 — 比較兩種工作模式

> 執行日期：2026-10-18｜環境：Windows 10、Python 3.14.3、pytest 8.4.2
> Chat 那一側**未實際開 claude.ai**，依一般使用經驗描述；Claude Code 那一側是**真的執行**的紀錄。

## 任務 1：兩種模式實測

### Claude Chat（依常識描述）

輸入「請幫我建立一個 hello.py」，Chat 會回一段文字，內容通常是：

````text
這是一個簡單的 hello.py：

```python
print("Hello, World!")
```

存檔後在終端機執行 `python hello.py` 即可。
````

- 磁碟上**沒有任何檔案**被建立。
- 使用者要自己複製、開編輯器、存檔、開終端機執行。
- Chat 不知道你的資料夾長怎樣、不知道 Python 版本，也看不到執行結果。

### Claude Code（實際執行）

同樣的需求，Claude Code 直接在工作目錄建出 `hello.py`，接著自己執行驗證：

```text
$ python hello.py
Hello World
```

- 檔案**真的存在**：`hello.py`（9 行，含 `main()` 與 `if __name__ == "__main__":`）。
- 不用使用者複製貼上，執行結果也由 Claude Code 自己看到並回報。

### 差異比較

| 面向 | Claude Chat | Claude Code |
| --- | --- | --- |
| 產出 | 一段程式碼文字 | 磁碟上的實際檔案 |
| 誰動手 | 使用者自己存檔、執行 | Claude 自己建檔、執行 |
| 環境感知 | 看不到你的檔案與環境 | 可讀目錄、看版本、看執行輸出 |
| 驗證 | 無，靠使用者回報錯誤 | 自己跑程式確認結果 |
| 本質 | 「顧問」：告訴你怎麼做 | 「代理人（agent）」：替你做完 |

一句話：**Chat 給答案，Code 給結果。**

## 任務 2：識別工具呼叫

本次完成練習時，Claude Code 實際呼叫過的工具：

| # | 工具 | 這次做了什麼 | 少了它會失敗嗎？ |
| --- | --- | --- | --- |
| 1 | **Bash** | `cat` 讀兩份題目、`python --version` 確認環境；執行 `python hello.py`、`python main.py 3 + 4`、`pytest`；建立 `answer/` 目錄；最後 `git add` / `git commit` | **會**。沒有 Bash 就無法執行程式與測試，只能「寫」不能「驗證」，也無法 commit |
| 2 | **Write** | 建立 `hello.py`、`calculator/main.py`、`utils.py`、`tests/test_calc.py`，以及本解答與 NOTES.md | **會**（建立新檔的主要手段）。理論上可用 Bash 的 heredoc 代替，但較易出錯（引號、編碼） |
| 3 | **Read** | 這次題目改用 Bash `cat` 讀，所以 Read 沒被用到；平常讀檔、看圖片、讀 PDF 會用它 | **不一定**。有 Bash 時可以用 `cat` 代替；但兩者都沒有就完全看不到既有程式，修改既有檔案必失敗 |
| 4 | **Edit**（本次未用） | 修改既有檔案的部分內容（精準字串替換） | 本次全是新檔，所以不影響；改舊檔時少了它只能整檔重寫 |

觀察重點：

- 工具名稱會出現在終端機每一步的標頭（例如 `Bash(python hello.py)`、`Write(calculator/utils.py)`），可以藉此追蹤 Claude 到底做了哪些動作。
- 工具之間有**替代性**（Bash 可以部分代替 Read/Write），但**缺少「能執行」的工具（Bash）時，agent 就失去自我驗證的能力**，退化成跟 Chat 差不多。
- 工具就是 agent 的「手腳」：模型負責決定，工具負責真正改變世界。
