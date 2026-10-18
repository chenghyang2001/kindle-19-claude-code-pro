"""寄送層：dry-run 只印出，real 模式才連 SMTP。帳密一律從環境變數讀。"""
import os
import smtplib
import time
from email.message import EmailMessage

REQUIRED_ENV = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD")
# Gmail 等服務對短時間大量寄信會暫時封鎖，固定間隔 1 秒
SEND_INTERVAL_SECONDS = 1.0


def build_message(sender: str, to: str, subject: str, body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = sender, to, subject
    msg.set_content(body)
    return msg


def check_smtp_env() -> dict[str, str]:
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"缺少環境變數：{', '.join(missing)}（請參考 .env.example）")
    return {k: os.environ[k] for k in REQUIRED_ENV}


def send_all(messages: list[EmailMessage], dry_run: bool = True) -> int:
    """寄出所有信件，回傳成功數。dry_run=True 時完全不連網路。"""
    if dry_run:
        for msg in messages:
            print(f"[DRY-RUN] To={msg['To']} Subject={msg['Subject']}")
        return len(messages)
    env = check_smtp_env()
    sent = 0
    with smtplib.SMTP(env["SMTP_HOST"], int(env["SMTP_PORT"]), timeout=30) as smtp:
        smtp.starttls()
        smtp.login(env["SMTP_USER"], env["SMTP_PASSWORD"])
        for msg in messages:
            try:
                smtp.send_message(msg)
                sent += 1
            except smtplib.SMTPException as exc:
                print(f"[FAIL] {msg['To']}：{exc}")
            time.sleep(SEND_INTERVAL_SECONDS)
    return sent
