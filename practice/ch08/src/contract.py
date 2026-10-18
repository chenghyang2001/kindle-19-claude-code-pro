"""合約驗證工具：用 jsonschema 驗證 agent 之間傳遞的 JSON。

用法：
    python src/contract.py contracts/research_output.schema.json samples/research_valid.json
回傳碼：0=合格、1=不合格、2=檔案或 JSON 讀取錯誤
"""
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = PROJECT_ROOT / "contracts"


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_validator(schema_name: str) -> Draft202012Validator:
    """載入 contracts/ 下的 schema；先檢查 schema 本身合法，避免合約寫錯卻靜默放行。"""
    schema = load_json(CONTRACTS_DIR / schema_name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def collect_errors(validator: Draft202012Validator, payload: Any) -> list[str]:
    """回傳人看得懂的錯誤清單（含 JSON 路徑），空清單代表合格。"""
    errors = sorted(validator.iter_errors(payload), key=lambda e: [str(p) for p in e.absolute_path])
    return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in errors]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("用法：python src/contract.py <schema.json> <data.json>", file=sys.stderr)
        return 2
    try:
        validator = load_validator(Path(argv[1]).name)
        payload = load_json(Path(argv[2]))
    except (OSError, json.JSONDecodeError) as err:
        print(f"讀取失敗：{err}", file=sys.stderr)
        return 2
    errors = collect_errors(validator, payload)
    if not errors:
        print(f"PASS  {argv[2]} 符合 {argv[1]}")
        return 0
    print(f"FAIL  {argv[2]} 有 {len(errors)} 個違規：")
    for line in errors:
        print(f"  - {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
