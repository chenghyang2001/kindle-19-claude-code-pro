"""練習 02：研究 agent → 寫作 agent 的合約協作與錯誤處理模擬。

研究 agent 用 mock 取代真實 LLM／網路呼叫（不需任何帳號），可切換 5 種行為：
ok / error（網路失敗）/ empty（查無資料）/ malformed（格式違約）/ flaky（前兩次空、第三次成功）。

錯誤處理策略：
1. error   → 研究端回傳 status=error 信封；retryable 才重試；用盡後寫作端「停止」並回報
2. empty   → 最多重試 2 次（共 3 次）並放寬查詢；仍空 → 寫作端 fallback 成「大綱 + 待補資料」草稿
3. malformed → 以 research_output.schema.json 驗證；整體信封壞 → 停止；
               只有部分 finding 壞 → 丟棄壞的、保留好的（partial），低於門檻才停止
"""
import copy
import json
import sys
from datetime import datetime, timezone

from contract import PROJECT_ROOT, collect_errors, load_validator

MAX_ATTEMPTS = 3            # 首次 + 重試 2 次
MIN_VALID_FINDINGS = 1      # partial data 至少要剩幾筆才繼續寫

PRODUCER = load_validator("research_output.schema.json")
CONSUMER = load_validator("writer_input.schema.json")


class ResearchFailed(Exception):
    """研究 agent 無法產出可用結果，寫作 agent 必須停止。"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def mock_research_agent(topic: str, mode: str, attempt: int) -> dict:
    """模擬研究 agent。真實版本會呼叫搜尋 API／LLM，這裡只回固定資料。"""
    with open(PROJECT_ROOT / "samples" / "research_valid.json", encoding="utf-8") as fh:
        base = json.load(fh)
    base.update(topic=topic, generated_at=now_iso(), attempts=attempt)
    if mode == "ok" or (mode == "flaky" and attempt >= 3):
        return base
    if mode in ("empty", "flaky"):
        return {**{k: base[k] for k in ("contract_version", "topic", "generated_at")},
                "status": "empty", "findings": [], "attempts": attempt}
    if mode == "error":
        return {"contract_version": "1.0", "status": "error", "topic": topic,
                "generated_at": now_iso(), "attempts": attempt,
                "error": {"code": "TIMEOUT", "message": "search API 30s timeout", "retryable": True}}
    if mode == "malformed":
        broken = copy.deepcopy(base)
        broken["findings"][1]["confidence"] = 7          # 一筆壞掉：可信度超出 0~1
        broken["findings"][1].pop("sources")              # 且缺來源
        return broken
    if mode == "garbage":
        return {"oops": "not a contract"}                 # 信封整個壞掉
    raise ValueError(f"未知 mode：{mode}")


def salvage_findings(payload: dict) -> tuple[list, list]:
    """逐筆驗 finding，回傳 (合格, 被丟棄的錯誤說明)。"""
    finding_schema = PRODUCER.schema["$defs"]["finding"]
    validator = PRODUCER.evolve(schema={**finding_schema, "$defs": PRODUCER.schema["$defs"]})
    kept, dropped = [], []
    for idx, finding in enumerate(payload.get("findings") or []):
        errors = collect_errors(validator, finding)
        if errors:
            dropped.append(f"findings[{idx}] 丟棄：{errors[0]}")
        else:
            kept.append(finding)
    return kept, dropped


def run_research(topic: str, mode: str) -> tuple[dict, list[str]]:
    """呼叫研究 agent，含重試與合約驗證。回傳 (給寫作端的資料, 事件紀錄)。"""
    events: list[str] = []
    query = topic
    for attempt in range(1, MAX_ATTEMPTS + 1):
        payload = mock_research_agent(query, mode, attempt)
        errors = collect_errors(PRODUCER, payload)
        status = payload.get("status")
        events.append(f"第 {attempt} 次：status={status} 違規={len(errors)}")

        if errors:
            kept, dropped = salvage_findings(payload)
            events.extend(dropped)
            envelope_ok = all(k in payload for k in ("topic", "status")) and status == "ok"
            if envelope_ok and len(kept) >= MIN_VALID_FINDINGS:
                events.append(f"partial：保留 {len(kept)} 筆、丟棄 {len(dropped)} 筆，繼續寫作")
                return {**payload, "findings": kept, "partial": True}, events
            raise ResearchFailed(f"合約違規且無法挽救：{errors[:2]}")

        if status == "ok":
            return payload, events
        if status == "error":
            if not payload["error"]["retryable"] or attempt == MAX_ATTEMPTS:
                raise ResearchFailed(f"研究 agent 失敗：{payload['error']['code']}")
            continue
        if status == "empty":
            query = f"{topic}（放寬關鍵字 v{attempt}）"   # 重試時放寬查詢條件
            if attempt == MAX_ATTEMPTS:
                events.append("重試用盡仍無資料 → fallback 大綱模式")
                return {**payload, "topic": topic, "fallback": True}, events
    raise ResearchFailed("不應到達此處")


def writer_agent(data: dict) -> str:
    """寫作 agent：只依賴 writer_input 合約（寬鬆）；fallback 時輸出待補資料的大綱。"""
    if data.get("fallback"):
        return f"# {data['topic']}\n\n> ⚠️ 查無研究資料，以下為大綱草稿，待人工補充。\n\n## 背景\n## 重點\n## 結論\n"
    errors = collect_errors(CONSUMER, data)
    if errors:
        raise ResearchFailed(f"寫作端輸入不符：{errors}")
    lines = [f"# {data['topic']}", ""]
    if data.get("partial"):
        lines.append("> 注意：部分研究資料因格式不符被排除。\n")
    for finding in data["findings"]:
        confidence = finding.get("confidence", 0.5)
        lines.append(f"## {finding['title']}（可信度 {confidence:.0%}）")
        lines.extend(f"- {point}" for point in finding["key_points"])
        lines.append("")
    return "\n".join(lines)


def orchestrate(topic: str, mode: str) -> dict:
    """主流程：研究 → 驗證 → 寫作；回傳結果摘要，失敗也回傳而不是讓整個程式崩潰。"""
    try:
        data, events = run_research(topic, mode)
        article = writer_agent(data)
        outcome = "fallback" if data.get("fallback") else ("partial" if data.get("partial") else "ok")
        return {"mode": mode, "outcome": outcome, "events": events, "article": article}
    except ResearchFailed as err:
        return {"mode": mode, "outcome": "stopped", "events": [str(err)], "article": None}


def main() -> None:
    expected = {"ok": "ok", "error": "stopped", "empty": "fallback",
                "flaky": "ok", "malformed": "partial", "garbage": "stopped"}
    failures = 0
    for mode, want in expected.items():
        result = orchestrate("sub-agent 合約設計", mode)
        mark = "PASS" if result["outcome"] == want else "FAIL"
        failures += mark == "FAIL"
        print(f"[{mark}] mode={mode:<9} → outcome={result['outcome']:<8}（預期 {want}）")
        for event in result["events"]:
            print(f"        · {event}")
        if mode in ("malformed", "empty") and result["article"]:
            print("        --- 文章前 3 行 ---")
            for line in result["article"].splitlines()[:3]:
                print(f"        | {line}")
    if failures:
        print(f"\n{failures} 個情境不符預期", file=sys.stderr)
        sys.exit(1)
    print("\n6 個情境全部符合預期")


if __name__ == "__main__":
    main()
