"""信件重要度評分（1-5 分，規則式，不呼叫外部 API）。"""
import re
from dataclasses import dataclass, field

VIP_SENDERS = {"boss@acme.com", "ceo@acme.com", "alice@partner.com"}
URGENT_KEYWORDS = ("urgent", "asap", "緊急", "重要")
REPLY_HINTS = ("請確認", "請回覆", "回覆", "可以嗎", "是否", "please confirm", "let me know")
LONG_BODY_CHARS = 80  # 中文信件 80 字以上通常是需要處理的正式內容
URGENT_THRESHOLD = 4

DEADLINE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",
    r"今天\s*\d{1,2}:\d{2}",
    r"今天下班前",
    r"下週[一二三四五六日]",
    r"明天",
]


@dataclass
class EmailScore:
    score: int
    reasons: list[str] = field(default_factory=list)
    requires_reply: bool = False
    deadline: str | None = None

    @property
    def is_urgent(self) -> bool:
        return self.score >= URGENT_THRESHOLD


def extract_deadline(text: str) -> str | None:
    for pattern in DEADLINE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def detect_requires_reply(text: str) -> bool:
    lowered = text.lower()
    return "?" in text or "？" in text or any(h in lowered for h in REPLY_HINTS)


def score_email(email: dict) -> EmailScore:
    """依寄件人、關鍵字、是否需回覆、截止日、長度、附件加分，結果夾在 1-5。"""
    subject = email.get("subject") or ""
    body = email.get("body") or ""
    full_text = f"{subject}\n{body}"
    points, reasons = 1, []

    if (email.get("sender") or "").lower() in VIP_SENDERS:
        points += 1
        reasons.append("重要聯絡人")
    if any(k in subject.lower() for k in URGENT_KEYWORDS):
        points += 2
        reasons.append("主旨含緊急關鍵字")
    requires_reply = detect_requires_reply(full_text)
    if requires_reply:
        points += 1
        reasons.append("需要回覆")
    deadline = extract_deadline(full_text)
    if deadline is not None:
        points += 1
        reasons.append(f"有截止日：{deadline}")
    if len(body) >= LONG_BODY_CHARS:
        points += 1
        reasons.append("長信")
    if email.get("has_attachment") is True:
        points += 1
        reasons.append("有附件")

    if not reasons:
        reasons.append("無特別訊號")
    return EmailScore(score=max(1, min(5, points)), reasons=reasons,
                      requires_reply=requires_reply, deadline=deadline)
