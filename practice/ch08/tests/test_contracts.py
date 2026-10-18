"""合約與錯誤處理的 pytest：正常、邊界、錯誤三類案例。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from contract import PROJECT_ROOT, collect_errors, load_json, load_validator  # noqa: E402
from ex02_orchestrator import orchestrate  # noqa: E402

PRODUCER = load_validator("research_output.schema.json")
CONSUMER = load_validator("writer_input.schema.json")
VALID = load_json(PROJECT_ROOT / "samples" / "research_valid.json")
INVALID = load_json(PROJECT_ROOT / "samples" / "research_invalid.json")


def test_valid_sample_passes():
    assert collect_errors(PRODUCER, VALID) == []


def test_invalid_sample_fails_with_expected_reasons():
    joined = "\n".join(collect_errors(PRODUCER, INVALID))
    for keyword in ("contract_version", "sources", "author", "confidence", "key_points", "topic"):
        assert keyword in joined


def test_ok_status_requires_at_least_one_finding():
    payload = {**VALID, "findings": []}
    assert any("non-empty" in e or "should be non-empty" in e for e in collect_errors(PRODUCER, payload))


def test_error_status_requires_error_object():
    payload = {k: VALID[k] for k in ("contract_version", "topic", "generated_at")} | {"status": "error"}
    assert any("'error' is a required property" in e for e in collect_errors(PRODUCER, payload))


def test_bad_datetime_is_rejected():
    payload = {**VALID, "generated_at": "昨天下午"}
    assert any("date-time" in e for e in collect_errors(PRODUCER, payload))


def test_consumer_is_tolerant_of_extra_fields():
    """寫作端合約寬鬆：研究端新增欄位不會讓寫作端壞掉（降低耦合）。"""
    payload = {**VALID, "new_field_from_v1_1": "ok"}
    assert collect_errors(CONSUMER, payload) == []
    assert collect_errors(PRODUCER, payload) != []   # 但生產端嚴格版會擋


@pytest.mark.parametrize("mode,expected", [
    ("ok", "ok"), ("error", "stopped"), ("empty", "fallback"),
    ("flaky", "ok"), ("malformed", "partial"), ("garbage", "stopped"),
])
def test_failure_scenarios(mode, expected):
    result = orchestrate("sub-agent 合約設計", mode)
    assert result["outcome"] == expected
    if expected == "fallback":
        assert result["article"].startswith("# sub-agent 合約設計\n")
