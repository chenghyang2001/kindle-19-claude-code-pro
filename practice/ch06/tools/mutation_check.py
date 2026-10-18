"""簡易突變測試：把 starter 函式故意改壞，確認生成的測試會失敗（殺死突變）。"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "starter" / "alert_level.py"
TEST_FILE = "tests/test_alert_level_generated.py"

# (說明, 原字串, 改壞後字串)
MUTANTS = [
    ("門檻上限含→不含", "if avg <= limit", "if avg < limit"),
    ("有效比例 < 改 <=", "valid_ratio < min_valid_ratio", "valid_ratio <= min_valid_ratio"),
    ("有效下限 0 改 >0", "VALID_MIN <= r", "VALID_MIN < r"),
    ("有效上限 500 改 <500", "r <= VALID_MAX", "r < VALID_MAX"),
    ("移除 bool 檢查", "isinstance(value, bool) or ", ""),
    ("均值不四捨五入", "round(sum(valid) / len(valid), 1)", "sum(valid) / len(valid)"),
    ("fault_count 恆為 0", "sum(1 for r in readings if r == FAULT_CODE)", "0"),
    ("ratio 允許 0", "if not 0 < min_valid_ratio <= 1", "if not 0 <= min_valid_ratio <= 1"),
    ("危害等級改名", 'HAZARDOUS = "危害"', 'HAZARDOUS = "非常不健康"'),
    ("valid_ratio 不四捨五入", '"valid_ratio": round(valid_ratio, 2), "fault_count": fault_count}\n\n    avg',
     '"valid_ratio": valid_ratio, "fault_count": fault_count}\n\n    avg'),
]


def run_tests() -> bool:
    """回傳測試是否全部通過。"""
    proc = subprocess.run([sys.executable, "-m", "pytest", TEST_FILE, "-q", "-p", "no:cacheprovider"],
                          cwd=ROOT, capture_output=True, encoding="utf-8")
    return proc.returncode == 0


def main() -> int:
    original = TARGET.read_text(encoding="utf-8")
    backup = TARGET.with_suffix(".py.bak")
    shutil.copy(TARGET, backup)
    killed = 0
    try:
        for desc, old, new in MUTANTS:
            if old not in original:
                print(f"[略過] {desc}：找不到原字串")
                continue
            TARGET.write_text(original.replace(old, new, 1), encoding="utf-8")
            survived = run_tests()
            killed += not survived
            print(f"[{'存活 ✗' if survived else '殺死 ✓'}] {desc}")
    finally:
        shutil.move(backup, TARGET)
    print(f"突變分數：{killed}/{len(MUTANTS)}")
    return 0 if run_tests() else 1  # 確認原檔已還原且測試仍通過


if __name__ == "__main__":
    sys.exit(main())
