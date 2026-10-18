"""用 yaml.safe_load 驗證專案內所有 YAML 可解析，並檢查 ci.yml 與多環境設定的結構。"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".venv", ".git", "node_modules", ".pytest_cache", ".ruff_cache"}


def find_yaml_files(root: Path) -> list[Path]:
    """找出所有 .yml / .yaml，略過虛擬環境等目錄。"""
    files = [p for ext in ("*.yml", "*.yaml") for p in root.rglob(ext)]
    return sorted(p for p in files if not SKIP_DIRS & set(p.relative_to(root).parts))


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_triggers(workflow: dict) -> dict:
    # YAML 1.1 會把裸的 on 解析成布林 True，所以兩種 key 都要找
    return workflow.get("on", workflow.get(True)) or {}


def check_ci_workflow(workflow: dict) -> list[str]:
    """回傳 ci.yml 不符題目要求的地方（空清單代表全部符合）。"""
    errors = []
    triggers = get_triggers(workflow)
    if (triggers.get("push") or {}).get("branches") != ["main"]:
        errors.append("push 觸發必須只針對 main")
    if "pull_request" not in triggers:
        errors.append("缺少 pull_request 觸發")

    jobs = workflow.get("jobs", {})
    for job, expected_need in (("test", None), ("lint", "test"), ("security", "lint")):
        if job not in jobs:
            errors.append(f"缺少 job：{job}")
            continue
        if jobs[job].get("needs") != expected_need:
            errors.append(f"{job}.needs 應為 {expected_need}，實際為 {jobs[job].get('needs')}")
        steps = jobs[job].get("steps", [])
        if not any(str(s.get("uses", "")).startswith("actions/cache@") for s in steps):
            errors.append(f"{job} 沒有 actions/cache 步驟")
    if str(workflow.get("env", {}).get("PYTHON_VERSION")) != "3.11":
        errors.append("PYTHON_VERSION 必須是 3.11")
    return errors


def check_env_configs(staging: dict, production: dict) -> list[str]:
    """兩環境變數名稱要一致、機密不可寫真值、feature flag 要 staging 開 production 關。"""
    errors = []
    s_vars, p_vars = staging.get("variables", {}), production.get("variables", {})
    if set(s_vars) != set(p_vars):
        errors.append(f"兩環境變數名稱不一致：{set(s_vars) ^ set(p_vars)}")
    for env_name, env_vars in (("staging", s_vars), ("production", p_vars)):
        for key, spec in env_vars.items():
            if spec.get("secret") and "value" in spec:
                errors.append(f"{env_name}.{key} 是機密，不可在檔案中寫 value")
    if s_vars.get("FEATURE_FLAG_NEW_UI", {}).get("value") != "true":
        errors.append("staging 的 FEATURE_FLAG_NEW_UI 應為 true")
    if p_vars.get("FEATURE_FLAG_NEW_UI", {}).get("value") != "false":
        errors.append("production 的 FEATURE_FLAG_NEW_UI 應為 false")
    return errors


def main() -> int:
    failures = 0
    for path in find_yaml_files(ROOT):
        rel = path.relative_to(ROOT).as_posix()
        try:
            load_yaml(path)
            print(f"[OK]   可解析  {rel}")
        except yaml.YAMLError as e:
            failures += 1
            print(f"[FAIL] 解析失敗 {rel}：{e}")

    env_dir = ROOT / "config" / "environments"
    checks = {
        "ci.yml 結構": check_ci_workflow(load_yaml(ROOT / ".github" / "workflows" / "ci.yml")),
        "多環境設定": check_env_configs(
            load_yaml(env_dir / "staging.yaml"), load_yaml(env_dir / "production.yaml")
        ),
    }
    for name, errors in checks.items():
        print(f"[{'OK' if not errors else 'FAIL'}]   {name}")
        for err in errors:
            print(f"         - {err}")
        failures += len(errors)
    print(f"\n結果：{'全部通過' if failures == 0 else f'{failures} 個問題'}")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, yaml.YAMLError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
