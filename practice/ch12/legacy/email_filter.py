"""過濾信件：丟掉促銷、垃圾、系統通知；擴充後可附加評分並依分數排序。"""
from email_scorer import score_email

SKIP_LABELS = {"PROMOTIONS", "SPAM", "UPDATES"}
SKIP_SENDER_PREFIX = ("noreply@", "no-reply@")


def filter_emails(emails):
    kept = []
    for email in emails:
        if email.get("labels") in SKIP_LABELS:
            continue
        if (email.get("sender") or "").startswith(SKIP_SENDER_PREFIX):
            continue
        kept.append(email)
    return kept


def filter_and_score(emails, min_score=1):
    """過濾後評分，丟掉低於 min_score 的信，並依分數由高到低排序。"""
    scored = []
    for email in filter_emails(emails):
        result = score_email(email)
        if result.score >= min_score:
            scored.append({**email, "score": result})
    return sorted(scored, key=lambda e: e["score"].score, reverse=True)
