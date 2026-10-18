"""摘要：取內文第一句（真實版會呼叫 Claude API，這裡用規則模擬，不連網）。"""
import re


def summarize(email, max_len=40):
    first = re.split(r"[。！？!?\n]", email["body"].strip())[0]
    return first[:max_len] + ("…" if len(first) > max_len else "")


def summarize_all(emails):
    results = []
    for email in emails:  # 逐封處理；真實版這裡是逐次 API 呼叫
        results.append({**email, "summary": summarize(email)})
    return results
