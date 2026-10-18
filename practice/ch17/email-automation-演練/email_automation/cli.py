"""命令列入口：python -m email_automation.cli --template ... --recipients ... [--send]"""
import argparse
import sys
from pathlib import Path

from .recipients import load_recipients
from .sender import build_message, send_all
from .templates import TemplateError, load_template, render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="批次寄送範本信件（預設 dry-run）")
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--recipients", type=Path, required=True)
    parser.add_argument("--sender", default="noreply@example.com")
    parser.add_argument("--send", action="store_true", help="真的寄出（需 SMTP 環境變數）")
    args = parser.parse_args(argv)
    try:
        subject_tpl, body_tpl = load_template(args.template)
        recipients, errors = load_recipients(args.recipients)
        messages = [
            build_message(args.sender, r["email"], render(subject_tpl, r), render(body_tpl, r))
            for r in recipients
        ]
    except (TemplateError, ValueError, OSError) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1
    for err in errors:
        print(f"[SKIP] {err}", file=sys.stderr)
    try:
        sent = send_all(messages, dry_run=not args.send)
    except RuntimeError as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1
    print(f"完成：{sent}/{len(messages)} 封，略過 {len(errors)} 筆")
    return 0


if __name__ == "__main__":
    sys.exit(main())
