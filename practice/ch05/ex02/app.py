"""示範用 Flask API：某些條件下會 500，而且錯誤被全域 handler 吞掉。"""
import logging
import sys

from flask import Flask, abort, jsonify, request

from request_logger import log_request

app = Flask(__name__)

USERS = {
    1: {"name": "Alice", "email": "Alice@Example.com"},
    2: {"name": "Bob"},  # 舊資料沒有 email → 觸發 500 的條件
}


@app.errorhandler(Exception)
def handle_any_error(exc):
    # 重現情境：只回「Internal Server Error」、什麼都沒 log，
    # 這正是 log 裡看不到原因的元凶之一。
    code = getattr(exc, "code", 500)
    if not isinstance(code, int):
        code = 500
    return jsonify(error="Internal Server Error" if code == 500 else str(exc)), code


@app.route("/api/users")
@log_request
def list_users():
    limit = int(request.args.get("limit", 10))
    return jsonify([{"id": uid, **u} for uid, u in list(USERS.items())[:limit]])


@app.route("/api/users/<int:user_id>")
@log_request
def get_user_email(user_id):
    if user_id not in USERS:
        abort(404)
    return jsonify(id=user_id, email=USERS[user_id]["email"].lower())


@app.route("/api/login", methods=["POST"])
@log_request
def login():
    body = request.get_json(silent=True) or {}
    return jsonify(ok=body.get("password") == "demo")


@app.route("/legacy/users/<int:user_id>")
def legacy_get_user_email(user_id):
    """沒套 decorator 的同一段邏輯，用來對照「只看到 500」的狀況。"""
    return jsonify(id=user_id, email=USERS[user_id]["email"].lower())


def setup_logging(log_file=None):
    """同時輸出到 stdout，和（選擇性）log 檔。"""
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5055
    log_file = sys.argv[2] if len(sys.argv) > 2 else None
    setup_logging(log_file)
    app.run(host="127.0.0.1", port=port)
