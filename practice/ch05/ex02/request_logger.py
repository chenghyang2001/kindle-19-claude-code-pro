"""Flask route 用的請求 logging decorator。

記錄：方法、路徑、參數、耗時（ms）、狀態碼；拋例外時記完整 traceback。
高流量時可用 make_log_request(sample_rate=...) 只抽樣成功請求，錯誤與慢請求一律記。
"""
import functools
import logging
import random
import time

from flask import make_response, request
from werkzeug.exceptions import HTTPException

SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "authorization"}


def _mask(params):
    """遮蔽敏感欄位，避免密碼、token 落進 log。"""
    return {k: ("***" if k.lower() in SENSITIVE_KEYS else v) for k, v in params.items()}


def _request_params(view_kwargs):
    """收集 path 參數、query string、JSON body（解析失敗就略過，不影響主流程）。"""
    params = {"path": dict(view_kwargs), "query": _mask(request.args.to_dict())}
    body = request.get_json(silent=True)
    if isinstance(body, dict):
        params["json"] = _mask(body)
    return params


def make_log_request(sample_rate=1.0, slow_ms=None, logger=None, rand=random.random):
    """產生 decorator。

    sample_rate：2xx/3xx 請求被記錄的機率（0~1）。
    slow_ms：超過此毫秒數的請求一律記錄（None 表示不啟用）。
    rand：亂數來源，測試時可注入固定值。
    4xx、5xx、例外一律記錄，不受抽樣影響。
    """
    if not 0.0 <= sample_rate <= 1.0:
        raise ValueError(f"sample_rate 必須介於 0 和 1，收到 {sample_rate}")
    log = logger or logging.getLogger("request")

    def decorator(view):
        @functools.wraps(view)  # 保留原函式名稱，否則多個 route 會撞 endpoint 名
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            line = f"{request.method} {request.path} params={_request_params(kwargs)}"
            try:
                response = make_response(view(*args, **kwargs))
            except HTTPException as exc:
                # abort(404) 這類是預期中的錯誤，不需要 traceback
                ms = (time.perf_counter() - start) * 1000
                log.warning("%s status=%s %.1fms", line, exc.code, ms)
                raise
            except Exception:
                ms = (time.perf_counter() - start) * 1000
                log.exception("%s status=500 %.1fms 未處理的例外", line, ms)
                raise  # 交回 Flask，維持原本的 500 行為

            ms = (time.perf_counter() - start) * 1000
            status = response.status_code
            is_slow = slow_ms is not None and ms >= slow_ms
            if status >= 400:
                log.warning("%s status=%s %.1fms", line, status, ms)
            elif is_slow or rand() < sample_rate:
                level = logging.WARNING if is_slow else logging.INFO
                log.log(level, "%s status=%s %.1fms%s", line, status, ms, " SLOW" if is_slow else "")
            return response

        return wrapper

    return decorator


log_request = make_log_request()
