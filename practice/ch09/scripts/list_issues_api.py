"""方式 B：直接呼叫 GitHub REST API 列出 open issues（唯讀 GET）。

用法：python scripts/list_issues_api.py [owner/repo]
Token：讀環境變數 GITHUB_TOKEN（公開 repo 可不設，但只有 60 次/小時額度）。
"""
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_REPO = "chenghyang2001/kindle-19-claude-code-pro"
API_ROOT = "https://api.github.com"


def build_request(repo: str) -> urllib.request.Request:
    """組 GET 請求；只允許 GET，避免誤用成寫入。"""
    if repo.count("/") != 1 or not all(repo.split("/")):
        raise ValueError(f"repo 格式應為 owner/name，收到：{repo!r}")
    url = f"{API_ROOT}/repos/{repo}/issues?state=open&per_page=30"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "k19-ch09-practice",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers, method="GET")


def fetch_open_issues(repo: str) -> list[dict]:
    """回傳 open issues（排除 PR，REST API 會把 PR 也算進 issues）。"""
    req = build_request(repo)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            items = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API 回傳 HTTP {e.code}：{e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"網路錯誤：{e.reason}") from e
    return [
        {"number": i["number"], "title": i["title"], "created_at": i["created_at"]}
        for i in items
        if "pull_request" not in i
    ]


def main() -> None:
    repo = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPO
    try:
        issues = fetch_open_issues(repo)
    except (ValueError, RuntimeError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"repo": repo, "open_issue_count": len(issues), "issues": issues},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
