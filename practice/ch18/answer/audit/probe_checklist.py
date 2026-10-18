"""附錄 C 清單的動態探測：對 ch15-sample 兩個版本跑 bandit 抓不到的項目，產生證據。

只 import、不修改 ch15-sample 的程式碼。執行：
    PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python answer/audit/probe_checklist.py
"""
import importlib.util
import os
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "ch15-sample"
os.environ.setdefault("APP_SECRET_KEY", "probe-only-fake-key")  # 探測用假密鑰


def load(name: str):
    """以不同模組名載入兩版 app.py，避免互相覆蓋。"""
    spec = importlib.util.spec_from_file_location(f"app_{name}", ROOT / name / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fresh_db(mod):
    conn = sqlite3.connect(":memory:")
    mod.init_db(conn)
    return conn


def try_call(fn, *args):
    """回傳 (成功?, 結果或例外類型)，讓探測不中斷。"""
    try:
        return True, fn(*args)
    except Exception as exc:  # 探測需要記錄任何例外類型
        return False, f"{type(exc).__name__}: {exc}"[:90]


def timing(mod, conn, username, rounds=5):
    start = time.perf_counter()
    for _ in range(rounds):
        mod.login(conn, username, "wrong")
    return (time.perf_counter() - start) / rounds * 1000


def probe(name: str) -> None:
    mod = load(name)
    conn = fresh_db(mod)
    print(f"\n===== {name} =====")

    # 輸入驗證：數字範圍 / 型別
    print("P1 get_user(2**64)              ->", try_call(mod.get_user, conn, 2**64))
    print("P2 get_user(-1)                 ->", try_call(mod.get_user, conn, -1))
    # 輸入驗證：字串長度（超長帳號是否被拒）
    print("P3 login('a'*100000, 'x')       ->", try_call(mod.login, conn, "a" * 100_000, "x"))
    # 參數注入：以 '-' 開頭的「主機名」是否被當成 ping 選項
    if hasattr(mod, "_is_valid_host"):
        for host in ["-t", "-l", "--help"]:
            print(f"P4 _is_valid_host({host!r:8})       ->", mod._is_valid_host(host))
    # 身份驗證：是否存在驗證 token / 登出的函式
    for fn in ["verify_token", "logout", "revoke_token", "reset_password"]:
        print(f"P5 has {fn:15}           ->", hasattr(mod, fn))
    # Token：同一使用者兩次登入的 token 是否相同（不具隨機性、無法撤銷）
    ok, t1 = try_call(mod.login, conn, "alice", "alice-pw")
    ok2, t2 = try_call(mod.login, conn, "alice", "alice-pw")
    print("P6 token 兩次相同              ->", t1 == t2, f"({t1!s:.24}...)")
    # 授權：一般使用者可否讀取 admin 資料（IDOR）— get_user 根本不收身分
    print("P7 get_user 參數               ->", mod.get_user.__code__.co_varnames[: mod.get_user.__code__.co_argcount])
    # 帳號列舉：存在 vs 不存在帳號的登入耗時差
    t_exist = timing(mod, conn, "alice")
    t_ghost = timing(mod, conn, "nobody-here")
    print(f"P8 登入耗時 存在帳號 {t_exist:7.2f} ms / 不存在帳號 {t_ghost:7.2f} ms  比值 {t_exist / max(t_ghost, 1e-6):.1f}x")
    # 頻率限制：連續 50 次錯誤登入是否被鎖
    for _ in range(50):
        mod.login(conn, "bob", "guess")
    print("P9 50 次錯誤後正確密碼仍可登入 ->", mod.login(conn, "bob", "bob-pw") is not None)
    # 帳號停用：schema 是否有狀態欄位
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)")]
    print("P10 users 欄位                  ->", cols)
    # 外部呼叫逾時：ping_host 原始碼是否帶 timeout=
    src = (ROOT / name / "app.py").read_text(encoding="utf-8")
    print("P11 subprocess 有 timeout=      ->", "timeout=" in src)
    print("P12 有 logging / print 敏感值   ->", "logging" in src, "print(" in src)


def main() -> None:
    print("Python", sys.version.split()[0])
    for name in ["vulnerable", "fixed"]:
        probe(name)
    deps = [p.name for p in ROOT.rglob("*") if p.name in {"requirements.txt", "pyproject.toml", "poetry.lock", "Pipfile.lock"}]
    print("\nP13 依賴鎖定檔                  ->", deps or "無")


if __name__ == "__main__":
    main()
