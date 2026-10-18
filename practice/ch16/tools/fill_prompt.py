"""把 prompts/ 內的模板填入變數，輸出可直接貼給 Claude 的完整提示詞。

用法：
    python tools/fill_prompt.py prompts/writing/explain-code.md \
        --var audience=產品經理 --var length="200 字以內" \
        --var-file code=samples/order_utils.py

變數缺漏時以 exit code 2 結束並列出缺少的變數，避免把 {{xxx}} 原樣送給 Claude。
"""
import argparse
import re
import sys
from pathlib import Path

VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
TEMPLATE_HEADING = "## 模板"
DELIMITER = "---"


def extract_template(markdown_text: str) -> str:
    """取出「## 模板」標題下、兩條 --- 之間的內容。"""
    lines = markdown_text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == TEMPLATE_HEADING)
    except StopIteration:
        raise ValueError("找不到「## 模板」段落")
    delimiter_rows = [i for i in range(start + 1, len(lines)) if lines[i].strip() == DELIMITER]
    if len(delimiter_rows) < 2:
        raise ValueError("「## 模板」下方需要兩條 --- 包住模板內容")
    body = lines[delimiter_rows[0] + 1 : delimiter_rows[1]]
    return "\n".join(body).strip()


def find_variables(template: str) -> list[str]:
    """依出現順序列出不重複的變數名稱。"""
    return list(dict.fromkeys(VAR_PATTERN.findall(template)))


def fill_template(template: str, values: dict[str, str]) -> str:
    """替換變數；有任何變數沒給值就拋 KeyError（列出全部缺漏）。"""
    missing = [name for name in find_variables(template) if name not in values]
    if missing:
        raise KeyError(", ".join(missing))
    return VAR_PATTERN.sub(lambda m: values[m.group(1)], template)


def parse_pairs(pairs: list[str], from_file: bool) -> dict[str, str]:
    """把 key=value 參數轉成 dict；from_file=True 時 value 視為檔案路徑。"""
    values = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"參數格式應為 key=value：{pair}")
        key, raw = pair.split("=", 1)
        values[key.strip()] = Path(raw).read_text(encoding="utf-8") if from_file else raw
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="填入 prompt 模板變數")
    parser.add_argument("template_file", help="prompts/ 底下的模板 .md")
    parser.add_argument("--var", action="append", default=[], help="key=value")
    parser.add_argument("--var-file", action="append", default=[], help="key=檔案路徑")
    parser.add_argument("--list-vars", action="store_true", help="只列出模板需要的變數")
    args = parser.parse_args()

    try:
        template = extract_template(Path(args.template_file).read_text(encoding="utf-8"))
        if args.list_vars:
            print("\n".join(find_variables(template)))
            return 0
        values = parse_pairs(args.var, from_file=False)
        values.update(parse_pairs(args.var_file, from_file=True))
        sys.stdout.write(fill_template(template, values) + "\n")
        return 0
    except KeyError as missing:
        print(f"錯誤：缺少變數 {missing}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as err:
        print(f"錯誤：{err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
