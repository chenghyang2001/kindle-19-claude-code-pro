"""驗證 claude -p 產出的程式碼：從 outputs/*.md 抽出 code block，實際執行並對照需求。

執行：PYTHONUTF8=1 python -m pytest tests/test_outputs.py -v
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
sys.path.insert(0, str(ROOT / "samples"))
from avg_bug import average_score as original_average  # noqa: E402
from discount import calc as original_calc  # noqa: E402


def code_blocks(output_name: str, lang: str) -> list[str]:
    """抽出指定 markdown 輸出中某語言的所有 code block。"""
    path = OUT / f"{output_name}.md"
    if not path.is_file():
        pytest.skip(f"尚未產生輸出：{path.name}（先跑 scripts/run_compare.py）")
    text = path.read_text(encoding="utf-8")
    return re.findall(rf"```{lang}\n(.*?)```", text, flags=re.S)


def load_namespace(code: str) -> dict:
    """以非 __main__ 身分執行程式碼，取得函式定義（不觸發檔案內的冒煙測試區塊）。"""
    namespace = {"__name__": "generated"}
    exec(compile(code, "<generated>", "exec"), namespace)
    return namespace


# ---------------- ex01 p1：重構後行為必須與原版完全一致 ----------------
GRID = [(p, t, q) for p in (0, 1, 9.99, 50, 100, 101) for t in (0, 1, 2, 3) for q in (0, 1, 10, 11, 20)]


@pytest.mark.parametrize("variant", ["ex01-p1-before", "ex01-p1-after"])
def test_p1_refactor_keeps_behavior(variant):
    namespace = load_namespace(code_blocks(variant, "python")[0])
    refactored = namespace.get("calculate_order_total") or namespace["calc"]
    for p, t, q in GRID:
        assert refactored(p, t, q) == original_calc(p, t, q), (p, t, q)


def test_p1_after_keeps_old_signature_and_type():
    """改寫版提示詞要求 calc(p, t, q) 仍可用；它還宣稱回傳型別與原版一致。"""
    namespace = load_namespace(code_blocks("ex01-p1-after", "python")[0])
    for p, t, q in GRID:
        new_value = namespace["calc"](p=p, t=t, q=q)
        assert type(new_value) is type(original_calc(p, t, q)), (p, t, q)


def test_p1_before_breaks_interface():
    """記錄發現：原版提示詞產出的重構把 calc 改名（呼叫端會壞），且回傳型別 int 變 float。"""
    namespace = load_namespace(code_blocks("ex01-p1-before", "python")[0])
    assert "calc" not in namespace
    assert type(namespace["calculate_order_total"](50, 3, 30)) is float
    assert type(original_calc(50, 3, 30)) is int


# ---------------- ex01 p2：修 bug，對照改寫版提示詞給的規格 ----------------
SPEC_CASES = [([80, 90, 100], 90.0), ([], None), ([80, None, 91], 85.5), ([None, None], None), ([0, 100], 50.0)]


def test_p2_original_bug_reproduces():
    with pytest.raises(ZeroDivisionError):
        original_average([])


@pytest.mark.parametrize("variant", ["ex01-p2-before", "ex01-p2-after"])
def test_p2_fix_meets_spec(variant):
    fixed = load_namespace(code_blocks(variant, "python")[0])["average_score"]
    for scores, expected in SPEC_CASES:
        assert fixed(scores) == expected, scores


def test_p2_after_own_asserts_pass():
    """改寫版要求附 4 個 assert；把它附的測試真的跑一次。"""
    blocks = code_blocks("ex01-p2-after", "python")
    namespace = load_namespace(blocks[0])
    exec(blocks[1], namespace)


# ---------------- ex01 p3：FastAPI 使用者 API，用 TestClient 實測 ----------------
@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    main_code = code_blocks("ex01-p3-after", "python")[0]
    (tmp_path / "main.py").write_text(main_code, encoding="utf-8")
    monkeypatch.setenv("JWT_SECRET", "test-secret-for-local-only-0123456789abcdef")
    spec = importlib.util.spec_from_file_location("generated_main", tmp_path / "main.py")
    assert spec is not None and spec.loader is not None, "無法載入產生的 main.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from fastapi.testclient import TestClient
    import jwt
    token = jwt.encode({"sub": "tester"}, os.environ["JWT_SECRET"], algorithm="HS256")
    return TestClient(module.app), {"Authorization": f"Bearer {token}"}, main_code


@pytest.mark.xfail(reason="2026-10-18 實測 138 行，模型自稱「約 115 行」，違反提示詞的 120 行限制")
def test_p3_line_limit(api_client):
    _, _, main_code = api_client
    assert main_code.count("\n") <= 120


def test_p3_auth_required(api_client):
    client, _, _ = api_client
    res = client.get("/users")
    assert res.status_code == 401
    assert res.headers["content-type"].startswith("application/problem+json")
    assert {"type", "title", "status", "detail"} <= res.json().keys()
    assert client.get("/users", headers={"Authorization": "Bearer bad"}).status_code == 401


def test_p3_crud_flow(api_client):
    client, auth, _ = api_client
    created = client.post("/users", json={"name": "Amy", "email": "amy@example.com"}, headers=auth)
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert client.get(f"/users/{user_id}", headers=auth).json()["name"] == "Amy"
    dup = client.post("/users", json={"name": "Bob", "email": "amy@example.com"}, headers=auth)
    assert dup.status_code == 409
    bad = client.post("/users", json={"name": "", "email": "nope"}, headers=auth)
    assert bad.status_code == 422 and bad.json()["status"] == 422
    page = client.get("/users?page=1&size=1", headers=auth).json()
    assert page["total"] == 1 and len(page["items"]) == 1
    upd = client.put(f"/users/{user_id}", json={"name": "Amy2", "email": "amy@example.com"}, headers=auth)
    assert upd.status_code == 200 and upd.json()["name"] == "Amy2"
    assert client.delete(f"/users/{user_id}", headers=auth).status_code == 204
    missing = client.get(f"/users/{user_id}", headers=auth)
    assert missing.status_code == 404 and missing.json()["status"] == 404


# ---------------- ex02：兩份 TS 修正版都要過 tsc --strict 且 runtime 行為正確 ----------------
TS_RUNTIME_CHECK = r"""
const m = require(process.argv[2]);
const results = {};
results.isAdmin = m.isAdmin({ id: 1, name: "a", role: "admin" }) === true;
results.emailNoValue = m.emailDomain({ id: 1, name: "a", role: "member" }) === undefined;
results.emailOk = m.emailDomain({ id: 1, name: "a", role: "member", email: "a@x.com" }) === "x.com";
try { m.parseUsers("{}"); results.parseRejectsObject = false; } catch { results.parseRejectsObject = true; }
try { m.parseUsers('[{"id":1}]'); results.parseRejectsBadItem = false; } catch { results.parseRejectsBadItem = true; }
let calls = 0;
globalThis.fetch = async () => { calls++; return { ok: false, status: 404, json: async () => ({ error: "nf" }) }; };
(async () => {
  for (let i = 0; i < 2; i++) { try { await m.fetchUser(7); } catch {} }
  results.http404Rejected = calls === 2;  // 第二次仍重抓 = 錯誤沒有被快取
  console.log(JSON.stringify(results));
})();
"""


@pytest.mark.skipif(shutil.which("npx") is None or shutil.which("node") is None, reason="需要 Node.js")
@pytest.mark.parametrize("variant", ["ex02-b-norole", "ex02-b-role"])
def test_ex02_fixed_ts(variant, tmp_path):
    ts_code = code_blocks(variant, "(?:ts|typescript)")
    fixed = max(ts_code, key=len)  # 修正版是最長的那段 TS
    (tmp_path / "user_service.ts").write_text(fixed, encoding="utf-8")
    npx = shutil.which("npx")
    compile_cmd = [npx, "tsc", "--strict", "--target", "es2022", "--lib", "es2022,dom",
                   "--module", "commonjs", "--outDir", str(tmp_path / "js"), str(tmp_path / "user_service.ts")]
    proc = subprocess.run(compile_cmd, capture_output=True, encoding="utf-8", errors="replace", cwd=ROOT)
    assert proc.returncode == 0, f"tsc --strict 失敗：\n{proc.stdout}{proc.stderr}"
    (tmp_path / "check.js").write_text(TS_RUNTIME_CHECK, encoding="utf-8")
    run = subprocess.run(["node", str(tmp_path / "check.js"), str(tmp_path / "js" / "user_service.js")],
                         capture_output=True, encoding="utf-8", errors="replace", timeout=60)
    assert run.returncode == 0, run.stderr
    results = json.loads(run.stdout.strip().splitlines()[-1])
    print(variant, results)
    assert all(results.values()), results


def test_ex02_original_ts_hides_bugs(tmp_path):
    """原始碼在 tsc --strict 下 0 錯誤；拿掉 `as string` 後編譯器就會抓到 isAdmin 的 bug。"""
    npx = shutil.which("npx")
    if npx is None:
        pytest.skip("需要 Node.js")
    original = (ROOT / "samples" / "user_service.ts").read_text(encoding="utf-8")
    base = [npx, "tsc", "--noEmit", "--strict", "--target", "es2022", "--lib", "es2022,dom"]
    (tmp_path / "a.ts").write_text(original, encoding="utf-8")
    assert subprocess.run([*base, str(tmp_path / "a.ts")], capture_output=True, cwd=ROOT).returncode == 0
    (tmp_path / "b.ts").write_text(original.replace("(user.role as string)", "user.role"), encoding="utf-8")
    proc = subprocess.run([*base, str(tmp_path / "b.ts")], capture_output=True, encoding="utf-8", cwd=ROOT)
    assert proc.returncode != 0 and "TS2367" in proc.stdout
