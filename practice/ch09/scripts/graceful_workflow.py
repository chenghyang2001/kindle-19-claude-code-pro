"""延伸思考示範：Gmail → 摘要 → Notion 流程，token 在中途過期時「優雅失敗」。

不連真實服務，用假的 step 函式模擬 MCP 呼叫，重點在流程控制：
1. 開跑前先 preflight 檢查所有服務的 auth（fail fast）
2. 每步結果寫入 checkpoint 檔，失敗時可從斷點續跑
3. 寫入類步驟帶 idempotency key，重跑不會重複建立任務
4. auth 錯誤 → 明確停止並回報，不用空結果「假裝成功」
"""
import json
import sys
import tempfile
from pathlib import Path


class AuthExpiredError(Exception):
    """模擬 MCP 回傳 401 / invalid_grant。"""


class FakeServices:
    """假的外部服務；expire_after 表示 Notion 在建第幾筆任務後 token 過期。"""

    def __init__(self, notion_expire_after: int | None = None):
        self.notion_expire_after = notion_expire_after
        self.notion_created: dict[str, str] = {}  # idempotency_key -> task_id

    def check_auth(self, service: str) -> bool:
        return True

    def gmail_search(self) -> list[dict]:
        return [{"id": f"m{i}", "subject": f"urgent #{i}", "body": f"內容 {i}"} for i in range(1, 4)]

    def notion_create(self, key: str, title: str) -> str:
        if key in self.notion_created:  # 已建過 → 直接回傳，不重複建立
            return self.notion_created[key]
        if self.notion_expire_after is not None and len(self.notion_created) >= self.notion_expire_after:
            raise AuthExpiredError("Notion token expired (401)")
        task_id = f"task-{len(self.notion_created) + 1}"
        self.notion_created[key] = task_id
        return task_id


def load_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {"done": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("警告：checkpoint 損毀，從頭開始", file=sys.stderr)
        return {"done": {}}


def run_workflow(svc: FakeServices, ckpt_path: Path) -> dict:
    """回傳 {status, created, pending, error}；status ∈ ok / partial_failed / preflight_failed。"""
    missing = [s for s in ("gmail", "notion") if not svc.check_auth(s)]
    if missing:
        return {"status": "preflight_failed", "created": [], "pending": [], "error": f"未授權：{missing}"}

    ckpt = load_checkpoint(ckpt_path)
    mails = svc.gmail_search()
    created, pending, error = [], [], None
    for mail in mails:
        key = f"gmail:{mail['id']}"  # idempotency key = 來源信件 ID
        if key in ckpt["done"]:
            created.append(ckpt["done"][key])
            continue
        try:
            task_id = svc.notion_create(key, f"[摘要] {mail['subject']}")
        except AuthExpiredError as e:
            error = str(e)
            pending = [m["id"] for m in mails if f"gmail:{m['id']}" not in ckpt["done"]]
            break
        ckpt["done"][key] = task_id
        ckpt_path.write_text(json.dumps(ckpt, ensure_ascii=False), encoding="utf-8")
        created.append(task_id)

    status = "partial_failed" if error else "ok"
    return {"status": status, "created": created, "pending": pending, "error": error}


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ckpt = Path(tmp) / "checkpoint.json"
        svc = FakeServices(notion_expire_after=1)

        r1 = run_workflow(svc, ckpt)
        print("第 1 次執行（第 2 筆時 token 過期）：", json.dumps(r1, ensure_ascii=False))
        assert r1["status"] == "partial_failed"
        assert r1["created"] == ["task-1"] and r1["pending"] == ["m2", "m3"]

        svc.notion_expire_after = None  # 模擬使用者重新登入後續跑
        r2 = run_workflow(svc, ckpt)
        print("第 2 次執行（重新授權後續跑）：", json.dumps(r2, ensure_ascii=False))
        assert r2["status"] == "ok"
        assert r2["created"] == ["task-1", "task-2", "task-3"]
        assert len(svc.notion_created) == 3, "不可重複建立任務"

        svc_bad = FakeServices()
        svc_bad.check_auth = lambda s: s != "notion"
        r3 = run_workflow(svc_bad, Path(tmp) / "c2.json")
        print("第 3 次執行（preflight 就發現 Notion 未授權）：", json.dumps(r3, ensure_ascii=False))
        assert r3["status"] == "preflight_failed" and not svc_bad.notion_created
    print("全部斷言通過")


if __name__ == "__main__":
    main()
