"""範本載入與渲染。用 string.Template 而非 f-string/eval，避免名單內容被當成程式碼執行。"""
from pathlib import Path
from string import Template


class TemplateError(ValueError):
    """範本格式錯誤或缺少變數。"""


def load_template(path: Path) -> tuple[str, str]:
    """讀取範本：第一行為 `Subject: ...`，空一行後為內文。回傳 (subject, body)。"""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TemplateError(f"找不到範本檔：{path}") from exc
    first_line, _, body = text.partition("\n")
    if not first_line.startswith("Subject:"):
        raise TemplateError(f"範本第一行必須是 'Subject: ...'：{path}")
    return first_line[len("Subject:"):].strip(), body.lstrip("\n")


def render(template_text: str, fields: dict[str, str]) -> str:
    """以 $name 語法填入欄位；缺欄位直接報錯，不寄出半成品信件。"""
    try:
        return Template(template_text).substitute(fields)
    except KeyError as exc:
        raise TemplateError(f"範本缺少欄位：{exc.args[0]}") from exc
