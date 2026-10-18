"""API 路由：健康檢查與待辦清單（記憶體儲存，demo 用）。"""

from flask import Blueprint, jsonify, request

bp = Blueprint("api", __name__, url_prefix="/api")

# demo 用記憶體儲存；正式版改成資料庫
_todos: list[dict] = []


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/todos")
def list_todos():
    return jsonify(data=_todos)


@bp.post("/todos")
def create_todo():
    payload = request.get_json(silent=True)
    if (
        payload is None
        or not isinstance(payload.get("title"), str)
        or not payload["title"].strip()
    ):
        return jsonify(error="title 為必填字串"), 400
    todo = {"id": len(_todos) + 1, "title": payload["title"].strip()}
    _todos.append(todo)
    return jsonify(data=todo), 201
