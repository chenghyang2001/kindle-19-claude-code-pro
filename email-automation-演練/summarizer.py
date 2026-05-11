"""
summarizer.py — 呼叫 Claude CLI 將電子郵件摘要為結構化 JSON

用途：接收一封 email dict，透過 subprocess 呼叫 `claude -p` 取得
      JSON 格式的摘要結果，並將 detected_deadline 標準化為 YYYY-MM-DD。
"""

import json
import re
import subprocess
import sys
from datetime import date, timedelta


# 星期名稱對應 Python weekday（週一=0 … 週日=6）
_WEEKDAY_MAP: dict[str, int] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# 代表「立即」的關鍵字，均轉為今天日期
_TODAY_KEYWORDS: frozenset[str] = frozenset(
    ["asap", "immediately", "urgent", "today", "eod", "end of day"]
)


def _parse_deadline(deadline_str: str | None) -> str | None:
    """
    將自然語言截止日期字串轉換為 YYYY-MM-DD 格式。

    為何需要此函式：Claude 回傳的截止日期是人類可讀的英文（如 "Thursday EOD"），
    必須轉成標準日期才能讓下游（Notion / Telegram）正確排序與提醒。

    Args:
        deadline_str: 自然語言日期字串，或 None。

    Returns:
        ISO 格式日期字串（YYYY-MM-DD），無法解析時回傳 None。
    """
    if deadline_str is None:
        return None

    cleaned = deadline_str.strip().lower()

    # 空字串或明確無期限的寫法
    if not cleaned or cleaned in {"none", "n/a"}:
        return None

    today = date.today()

    # 「立即」類關鍵字 → 今天
    if cleaned in _TODAY_KEYWORDS:
        return today.isoformat()

    # "tomorrow" → 明天
    if cleaned == "tomorrow":
        return (today + timedelta(days=1)).isoformat()

    # 星期名稱：找下一個對應的週幾（若今天剛好是該天，則取下週同一天）
    for weekday_name, weekday_num in _WEEKDAY_MAP.items():
        if weekday_name in cleaned:
            days_ahead = (weekday_num - today.weekday()) % 7
            # 今天本身不算「下一個」，確保至少推進一天
            if days_ahead == 0:
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).isoformat()

    # 已是 ISO 格式（YYYY-MM-DD）
    iso_pattern = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", cleaned)
    if iso_pattern:
        try:
            parsed = date(
                int(iso_pattern.group(1)),
                int(iso_pattern.group(2)),
                int(iso_pattern.group(3)),
            )
            return parsed.isoformat()
        except ValueError:
            # 日期數值不合法（如 2026-13-01）
            return None

    # 無法識別的格式
    return None


def summarize_email(email: dict) -> dict | None:
    """
    呼叫 Claude CLI 對單封電子郵件產生結構化摘要。

    為何用 subprocess 而非 API：沿用 Max 訂閱額度（不消耗 API Credits），
    符合 cost-rules.md 的成本保護原則。

    Args:
        email: 包含 sender、subject、body 欄位的字典。

    Returns:
        包含 one_liner / full_summary / action_required /
        detected_deadline / priority_score 的字典；
        失敗時回傳 None。
    """
    sender = email.get("sender", "")
    subject = email.get("subject", "")
    body = email.get("body", "")

    prompt = (
        "Summarize this email. Respond in JSON format only. "
        "No preamble, no explanation.\n\n"
        "Required JSON fields:\n"
        '- "one_liner": max 80 chars summary for Telegram notification\n'
        '- "full_summary": 2-3 sentences preserving full context for Notion task body\n'
        '- "action_required": specific action needed (e.g. "Reply with approval by EOD")\n'
        '- "detected_deadline": extracted deadline in plain English '
        '(e.g. "Thursday EOD"), or null\n'
        "- \"priority_score\": integer 1-5 (5=most urgent, 1=least urgent)\n\n"
        f"From: {sender}\n"
        f"Subject: {subject}\n\n"
        f"{body}"
    )

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )

        output = result.stdout

        # 從輸出中萃取第一個符合結構的 JSON 物件
        # 為何用 re 而非直接 json.loads：Claude 偶爾會在 JSON 前後夾帶說明文字
        match = re.search(
            r'\{[^{}]*"one_liner"[^{}]*\}',
            output,
            re.DOTALL,
        )
        if not match:
            print(
                f"[summarizer] 無法在輸出中找到 JSON 物件。stdout={output!r}",
                file=sys.stderr,
            )
            return None

        parsed: dict = json.loads(match.group(0))

        # 標準化截止日期
        raw_deadline = parsed.get("detected_deadline")
        parsed["detected_deadline"] = _parse_deadline(raw_deadline)

        # 確保 priority_score 是 1-5 的整數（Claude 偶爾回傳字串或超界值）
        try:
            score = int(parsed["priority_score"])
            parsed["priority_score"] = max(1, min(5, score))
        except (KeyError, ValueError, TypeError):
            # 若欄位完全缺失或型別非法，預設給中等優先度
            parsed["priority_score"] = 3

        return parsed

    except subprocess.TimeoutExpired:
        print("[summarizer] claude CLI 呼叫逾時（> 60s）", file=sys.stderr)
        return None
    except json.JSONDecodeError as exc:
        print(f"[summarizer] JSON 解析失敗：{exc}", file=sys.stderr)
        return None
    except KeyError as exc:
        print(f"[summarizer] 缺少必要欄位：{exc}", file=sys.stderr)
        return None
    except ValueError as exc:
        print(f"[summarizer] 數值錯誤：{exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Smoke test — 僅在直接執行此腳本時跑，不影響 import 使用
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Smoke Test：_parse_deadline ===\n")

    # TC1：星期名稱 "Thursday EOD" → 下一個週四
    result_thursday = _parse_deadline("Thursday EOD")
    print(f"TC1 'Thursday EOD' → {result_thursday}")
    assert result_thursday is not None, "TC1 FAIL: 應回傳非 None"
    target_thursday = date.fromisoformat(result_thursday)
    assert target_thursday.weekday() == 3, (
        f"TC1 FAIL: 應為週四（weekday=3），實際 weekday={target_thursday.weekday()}"
    )
    assert target_thursday > date.today(), "TC1 FAIL: 應為未來日期"
    print(f"  ✓ TC1 PASS（{result_thursday} 是下一個週四）\n")

    # TC2：None → None
    result_none = _parse_deadline(None)
    print(f"TC2 None → {result_none}")
    assert result_none is None, "TC2 FAIL: None 輸入應回傳 None"
    print("  ✓ TC2 PASS\n")

    # TC3：已知 ISO 格式 "2026-12-25" → "2026-12-25"
    result_iso = _parse_deadline("2026-12-25")
    print(f"TC3 '2026-12-25' → {result_iso}")
    assert result_iso == "2026-12-25", f"TC3 FAIL: 預期 '2026-12-25'，實際 '{result_iso}'"
    print("  ✓ TC3 PASS\n")

    print("=== 所有 smoke test PASS ===")
