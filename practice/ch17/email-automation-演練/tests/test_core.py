"""核心測試：正常、邊界、錯誤三類。"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from email_automation import cli
from email_automation.recipients import load_recipients
from email_automation.sender import build_message, check_smtp_env, send_all
from email_automation.templates import TemplateError, load_template, render

ROOT = Path(__file__).resolve().parent.parent


class TemplateTests(unittest.TestCase):
    def test_render_ok(self):
        self.assertEqual(render("Hi $name", {"name": "Bob"}), "Hi Bob")

    def test_render_missing_field(self):
        with self.assertRaises(TemplateError):
            render("Hi $name $course", {"name": "Bob"})

    def test_load_template(self):
        subject, body = load_template(ROOT / "templates" / "welcome.txt")
        self.assertIn("$name", subject)
        self.assertIn("$course", body)

    def test_missing_template_file(self):
        with self.assertRaises(TemplateError):
            load_template(ROOT / "templates" / "nope.txt")


class RecipientTests(unittest.TestCase):
    def test_invalid_and_duplicate_skipped(self):
        valid, errors = load_recipients(ROOT / "data" / "recipients.csv")
        self.assertEqual([r["email"] for r in valid], ["alice@example.com", "bob@example.com"])
        self.assertEqual(len(errors), 2)

    def test_csv_without_email_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("name\nBob\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_recipients(path)


class SenderTests(unittest.TestCase):
    def test_dry_run_never_touches_smtp(self):
        msg = build_message("a@example.com", "b@example.com", "s", "b")
        with mock.patch("smtplib.SMTP") as smtp:
            self.assertEqual(send_all([msg], dry_run=True), 1)
            smtp.assert_not_called()

    def test_missing_env_raises(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                check_smtp_env()


class CliTests(unittest.TestCase):
    def test_cli_dry_run_end_to_end(self):
        code = cli.main(["--template", str(ROOT / "templates" / "welcome.txt"),
                         "--recipients", str(ROOT / "data" / "recipients.csv")])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
