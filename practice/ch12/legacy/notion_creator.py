"""模擬建立 Notion 頁面：寫到 output/notion_pages.json（真實版用 Notion API，見範本）。"""
import json
from pathlib import Path


def create_pages(summaries, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = [{"title": s["subject"], "from": s["sender"], "summary": s["summary"]} for s in summaries]
    path = out_dir / "notion_pages.json"
    path.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
