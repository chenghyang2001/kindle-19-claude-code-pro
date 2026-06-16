# 練習 03 解答 — TDD 實戰：Email 驗證器

## 階段一：Red（先寫測試，全部 FAIL）⏱ ~5 分鐘

```python
# tests/test_email_validator.py
import pytest
from email_validator import is_valid_email

def test_valid_email_returns_true():
    assert is_valid_email("user@example.com") is True

def test_missing_at_symbol_returns_false():
    assert is_valid_email("userexample.com") is False

def test_multiple_at_symbols_returns_false():
    assert is_valid_email("user@@example.com") is False

def test_empty_string_returns_false():
    assert is_valid_email("") is False

def test_plus_tag_in_local_part_is_valid():
    assert is_valid_email("user+tag@example.com") is True
```

---

## 階段二：Green（最小實作，5 個測試全通過）⏱ ~5 分鐘

```python
# email_validator.py
def is_valid_email(email: str) -> bool:
    if not email:
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    local, domain = parts
    return bool(local) and bool(domain)
```

---

## 階段三：Refactor（改善品質，測試仍全通過）⏱ ~3 分鐘

```python
# email_validator.py
def is_valid_email(email: str) -> bool:
    """驗證 email 格式是否合法。

    合法條件：恰好一個 @，@ 前後都不為空。
    注意：不驗證 domain 格式（.com 等），只做基礎結構檢查。
    """
    if not email:
        return False
    if email.count("@") != 1:
        return False
    local, domain = email.split("@")
    return bool(local) and bool(domain)
```

**改動說明：**
- `len(split()) != 2` → `count("@") != 1`：意圖更直白，直接說「@ 不是剛好一個」
- 加 docstring 說明函式限制（不驗證 domain 格式）

---

## 反思問題

**1. 哪個階段最困難？**

Red 階段。要在沒有實作的情況下設計測試，等於逼自己先想清楚「這個函式的邊界在哪」。例如：`user+tag@example.com` 合不合法？不先想清楚，測試就會寫錯方向。

**2. Refactor 改了什麼？先實作後測試時會自然發生嗎？**

把 `split("@")` 的長度檢查改成 `count("@")` 更直白。先實作後測試時**不會自然發生**，因為「能跑通測試就算完成」，沒有外力逼你回頭改善。TDD 的 Refactor 階段明確要求「帶著安全網改善」。

**3. TDD 適合 vs. 不適合的情境**

| 適合 | 不適合 |
|------|--------|
| 邏輯邊界明確（驗證器、計算器） | 探索性功能（不知道輸出長什麼樣） |
| 業務規則複雜、易錯 | UI 互動、視覺設計 |
| 需要長期維護的核心模組 | 一次性腳本、快速 prototype |
| 多人協作、規格已確定 | 需要大量外部依賴的整合邏輯 |
