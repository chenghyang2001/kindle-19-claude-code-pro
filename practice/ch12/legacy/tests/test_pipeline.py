"""評分擴充的測試：正常、邊界、錯誤、整合。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from email_scorer import EmailScore, extract_deadline, score_email  # noqa: E402
from email_filter import filter_and_score, filter_emails  # noqa: E402
from gmail_fetcher import FetchError, fetch_emails  # noqa: E402
from run_briefing import run  # noqa: E402
from telegram_briefer import build_message  # noqa: E402


def make_email(**overrides):
    base = {"id": "x", "sender": "someone@x.com", "subject": "hi", "body": "hello",
            "received_at": "2026-10-17T00:00:00", "has_attachment": False, "labels": "INBOX"}
    base.update(overrides)
    return base


# --- 正常案例 ---
def test_urgent_vip_email_scores_5():
    email = make_email(sender="boss@acme.com", subject="URGENT: 報告",
                       body="請在今天 17:00 前寄給我，可以嗎？", has_attachment=True)
    result = score_email(email)
    assert result.score == 5
    assert result.is_urgent
    assert result.requires_reply is True
    assert result.deadline == "今天 17:00"
    assert "重要聯絡人" in result.reasons


def test_plain_email_scores_1():
    result = score_email(make_email())
    assert result.score == 1
    assert result.reasons == ["無特別訊號"]
    assert result.requires_reply is False
    assert result.deadline is None


def test_question_marks_require_reply():
    assert score_email(make_email(body="中午吃飯嗎？")).requires_reply is True
    assert score_email(make_email(body="lunch?")).requires_reply is True


def test_extract_iso_deadline():
    assert extract_deadline("截止日 2026-10-20。") == "2026-10-20"


# --- 邊界案例 ---
def test_score_clamped_to_5():
    email = make_email(sender="ceo@acme.com", subject="緊急 ASAP 重要",
                       body="請確認？" + "字" * 200 + " 2026-10-20", has_attachment=True)
    assert score_email(email).score == 5


def test_missing_fields_do_not_crash():
    result = score_email({"sender": None, "subject": None, "body": None})
    assert isinstance(result, EmailScore)
    assert result.score == 1


def test_empty_list():
    assert filter_and_score([]) == []


def test_long_body_threshold_boundary():
    assert "長信" not in score_email(make_email(body="字" * 79)).reasons
    assert "長信" in score_email(make_email(body="字" * 80)).reasons


def test_min_score_filters_and_sorts():
    emails = [make_email(id="low"), make_email(id="high", subject="urgent", sender="boss@acme.com")]
    result = filter_and_score(emails, min_score=2)
    assert [e["id"] for e in result] == ["high"]
    sorted_all = filter_and_score(emails)
    assert [e["id"] for e in sorted_all] == ["high", "low"]


def test_filter_drops_spam_and_noreply():
    emails = [make_email(labels="SPAM"), make_email(sender="noreply@github.com"), make_email(id="ok")]
    assert [e["id"] for e in filter_emails(emails)] == ["ok"]


def test_briefing_without_score_keeps_legacy_format():
    msg = build_message([{"subject": "s", "sender": "a@b.c", "summary": "x"}])
    assert "⭐" not in msg and "1. s — a@b.c" in msg


# --- 錯誤案例 ---
def test_missing_csv_raises_fetch_error(tmp_path):
    with pytest.raises(FetchError):
        fetch_emails(tmp_path / "nope.csv")


def test_csv_missing_columns_raises(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("id,sender\n1,a@b.c\n", encoding="utf-8")
    with pytest.raises(FetchError, match="缺少欄位"):
        fetch_emails(bad)


# --- 整合案例（使用 legacy/data/emails.csv，全部寫入 tmp_path，不連任何外部服務）---
def test_full_pipeline_with_scoring(tmp_path):
    result = run(out_dir=tmp_path)
    assert result["fetched"] == 7
    assert result["kept"] == 4
    assert len(result["alerts"]) == 3  # boss / alice / ceo 三封達 4 分以上
    assert (tmp_path / "telegram_message.txt").exists()
    assert (tmp_path / "telegram_urgent.txt").exists()
    assert (tmp_path / "notion_pages.json").exists()
    first_line = result["message"].splitlines()[1]
    assert first_line.startswith("1. ⭐⭐⭐⭐⭐")


def test_full_pipeline_no_score_matches_legacy(tmp_path):
    result = run(out_dir=tmp_path, use_score=False)
    assert result["kept"] == 4
    assert result["alerts"] == []
    assert "⭐" not in result["message"]
    assert not (tmp_path / "telegram_urgent.txt").exists()
