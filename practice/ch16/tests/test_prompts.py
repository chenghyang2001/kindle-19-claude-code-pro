"""驗證 prompts/ 下每個模板格式正確，且 fill_prompt 的正常 / 邊界 / 錯誤路徑都正常。"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import fill_prompt  # noqa: E402

PROMPT_FILES = sorted(p for p in (ROOT / "prompts").rglob("*.md") if p.name != "README.md" and "evolution" not in p.name)
REQUIRED_SECTIONS = ["## 用途", "## 變數", "## 模板", "## 範例填入", "## 預期輸出格式", "## 使用說明", "## 版本紀錄"]


def test_each_category_has_two_prompts():
    for category in ["code", "review", "writing", "debug"]:
        assert len(list((ROOT / "prompts" / category).glob("*.md"))) >= 2, category


@pytest.mark.parametrize("prompt_file", PROMPT_FILES, ids=lambda p: p.stem)
def test_prompt_file_structure(prompt_file):
    text = prompt_file.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in text, f"{prompt_file.name} 缺少 {section}"
    template = fill_prompt.extract_template(text)
    variables = fill_prompt.find_variables(template)
    assert variables, "模板至少要有一個 {{變數}}"
    # 變數表必須列出模板用到的每個變數
    for name in variables:
        assert f"`{{{{{name}}}}}`" in text, f"{prompt_file.name} 變數表缺少 {name}"


@pytest.mark.parametrize("prompt_file", PROMPT_FILES, ids=lambda p: p.stem)
def test_readme_indexes_every_prompt(prompt_file):
    readme = (ROOT / "prompts" / "README.md").read_text(encoding="utf-8")
    rel = prompt_file.relative_to(ROOT / "prompts").as_posix()
    assert rel in readme, f"README 沒有索引 {rel}"


def test_fill_happy_path():
    assert fill_prompt.fill_template("給 {{who}}：{{ msg }}", {"who": "PM", "msg": "嗨"}) == "給 PM：嗨"


def test_fill_edge_repeated_and_special_chars():
    # 值內含 regex 特殊字元與反斜線時不可被轉義
    assert fill_prompt.fill_template("{{a}}-{{a}}", {"a": r"\d+$"}) == r"\d+$-\d+$"


def test_fill_error_missing_variable():
    with pytest.raises(KeyError, match="b"):
        fill_prompt.fill_template("{{a}} {{b}}", {"a": "1"})


def test_extract_error_without_template_section():
    with pytest.raises(ValueError):
        fill_prompt.extract_template("# 沒有模板")
