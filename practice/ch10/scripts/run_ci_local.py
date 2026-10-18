"""在本機依 needs 順序執行 ci.yml 每個 job 的 run 指令（模擬 GitHub Actions，失敗即停止）。"""

import os
import subprocess  # nosec B404: 只執行本 repo ci.yml 裡的指令
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def job_order(jobs: dict) -> list[str]:
    """依 needs 做拓撲排序，確保 test → lint → security。"""
    ordered, pending = [], dict(jobs)
    while pending:
        ready = [
            name
            for name, job in pending.items()
            if all(n in ordered for n in _as_list(job.get("needs")))
        ]
        if not ready:
            raise ValueError(f"needs 有循環或指向不存在的 job：{list(pending)}")
        for name in ready:
            ordered.append(name)
            pending.pop(name)
    return ordered


def run_command(cmd: str, env: dict) -> int:
    print(f"  $ {cmd}")
    proc = subprocess.run(  # nosec B602: 指令來源是本 repo 的 ci.yml
        cmd,
        shell=True,
        cwd=ROOT,
        env=env,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    output = (proc.stdout + proc.stderr).strip()
    if output:
        print("    " + output[-1500:].replace("\n", "\n    "))
    return proc.returncode


def run_job(job_name: str, job: dict, env: dict) -> bool:
    for step in job.get("steps", []):
        if "run" not in step:
            print(f"  - 略過 uses: {step.get('uses')}（本機不需要）")
            continue
        for cmd in filter(None, (line.strip() for line in step["run"].splitlines())):
            code = run_command(cmd, env)
            if code != 0:
                print(f"  ✗ job {job_name} 失敗（exit {code}），後續 job 不執行")
                return False
    print(f"  ✓ job {job_name} 通過")
    return True


def main() -> int:
    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    workflow = yaml.safe_load(ci_path.read_text(encoding="utf-8"))
    env = dict(os.environ)
    venv_bin = ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    if venv_bin.exists():  # 讓 python 指向專案 venv，不污染全域套件
        env["PATH"] = f"{venv_bin}{os.pathsep}{env['PATH']}"
    env["PYTHONUTF8"] = "1"
    for name in job_order(workflow["jobs"]):
        print(f"\n=== job: {name} ===")
        if not run_job(name, workflow["jobs"][name], env):
            return 1
    print("\n全部 job 通過")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
