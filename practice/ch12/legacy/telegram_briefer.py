"""模擬 Telegram 簡報：組訊息並寫檔（dry-run，絕不真的送出）。擴充：顯示評分、緊急信另發一則。"""
from pathlib import Path


def build_message(summaries):
    lines = [f"📬 今日信件簡報（{len(summaries)} 封）"]
    for i, s in enumerate(summaries, 1):
        score_obj = s.get("score")
        stars = f"{'⭐' * score_obj.score} " if score_obj is not None else ""
        lines.append(f"{i}. {stars}{s['subject']} — {s['sender']}\n   {s['summary']}")
        if score_obj is not None and score_obj.deadline is not None:
            lines.append(f"   ⏰ 截止：{score_obj.deadline}")
    return "\n".join(lines)


def build_urgent_alert(email):
    """4-5 分信件的緊急通知格式：獨立一則、列出原因與是否需回覆。"""
    score_obj = email["score"]
    reply = "需要回覆" if score_obj.requires_reply else "不需回覆"
    deadline = score_obj.deadline if score_obj.deadline is not None else "未標示"
    reasons = "、".join(score_obj.reasons)
    return (
        f"🚨 緊急信件（{score_obj.score}/5）\n"
        f"寄件人：{email['sender']}\n主旨：{email['subject']}\n"
        f"摘要：{email['summary']}\n截止：{deadline}｜{reply}\n"
        f"原因：{reasons}"
    )


def send_briefing(summaries, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    message = build_message(summaries)
    (out_dir / "telegram_message.txt").write_text(message, encoding="utf-8")
    urgent = [s for s in summaries if s.get("score") is not None and s["score"].is_urgent]
    alerts = [build_urgent_alert(s) for s in urgent]
    if alerts:
        (out_dir / "telegram_urgent.txt").write_text("\n\n".join(alerts), encoding="utf-8")
    return message, alerts
