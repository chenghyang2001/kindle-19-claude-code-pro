<!-- prompt: ex01/p3-after | ok | 84.5s -->

## 1. 端點一覽表

| Method | Path | 說明 | 成功狀態碼 |
| --- | --- | --- | --- |
| GET | `/users?page=1&size=10` | 分頁列出使用者（`size` 上限 100），回傳 `items`、`total`、`page`、`size` | 200 |
| GET | `/users/{user_id}` | 取得單一使用者 | 200 |
| POST | `/users` | 建立使用者（email 重複時回 409） | 201 |
| PUT | `/users/{user_id}` | 整筆更新使用者 | 200 |
| DELETE | `/users/{user_id}` | 刪除使用者 | 204 |

所有端點都必須帶 `Authorization: Bearer <JWT>`。錯誤一律回 `application/problem+json`，可能的狀態碼有 401、404、409、422、500。

## 2. main.py

```python
"""使用者管理 REST API：FastAPI + Pydantic v2，記憶體儲存，JWT Bearer 認證，RFC 7807 錯誤格式"""
import logging
import os
from http import HTTPStatus
from itertools import count
from typing import Annotated

import jwt  # PyJWT
from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException  # FastAPI 的 HTTPException 繼承自它，404/405 也會進同一個 handler

JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("缺少環境變數 JWT_SECRET")
JWT_ALGORITHM = "HS256"
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"  # 不用 EmailStr，省掉 email-validator 依賴
logger = logging.getLogger("user-api")


# ---------- 資料模型 ----------
class UserIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=254)


class UserOut(UserIn):
    id: int


class Page(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    size: int


users: dict[int, UserOut] = {}
id_seq = count(1)


# ---------- 認證 ----------
bearer = HTTPBearer(auto_error=False)  # 關掉預設錯誤，才能統一回 RFC 7807 格式


def get_current_user(cred: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> dict:
    """驗證 Bearer JWT，成功回傳 payload；失敗一律 401。"""
    challenge = {"WWW-Authenticate": "Bearer"}
    if cred is None:
        raise HTTPException(401, "缺少 Bearer token", headers=challenge)
    try:
        return jwt.decode(cred.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "token 已過期", headers=challenge) from None
    except jwt.InvalidTokenError:
        raise HTTPException(401, "token 無效", headers=challenge) from None


# 掛在 app 層：所有 API 路由都要認證（/docs 與 /openapi.json 不受影響）
app = FastAPI(title="使用者管理 API", dependencies=[Depends(get_current_user)])


# ---------- RFC 7807 錯誤處理 ----------
def problem(request: Request, status: int, detail: str, headers: dict | None = None) -> JSONResponse:
    body = {"type": "about:blank", "title": HTTPStatus(status).phrase,
            "status": status, "detail": detail, "instance": request.url.path}
    return JSONResponse(body, status_code=status, headers=headers,
                        media_type="application/problem+json")


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException):
    return problem(request, exc.status_code, str(exc.detail), exc.headers)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    detail = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
    return problem(request, 422, detail)


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    logger.exception("未預期錯誤")  # 細節只寫 log，不回給客戶端
    return problem(request, 500, "伺服器內部錯誤")


# ---------- 共用輔助 ----------
def get_or_404(user_id: int) -> UserOut:
    user = users.get(user_id)
    if user is None:
        raise HTTPException(404, f"使用者 {user_id} 不存在")
    return user


def ensure_email_unique(email: str, exclude_id: int | None = None) -> None:
    if any(u.email == email and u.id != exclude_id for u in users.values()):
        raise HTTPException(409, f"email {email} 已被使用")


# ---------- 端點 ----------
@app.get("/users", response_model=Page)
def list_users(page: Annotated[int, Query(ge=1)] = 1,
               size: Annotated[int, Query(ge=1, le=100)] = 10):
    ordered = sorted(users.values(), key=lambda u: u.id)
    start = (page - 1) * size
    return Page(items=ordered[start:start + size], total=len(ordered), page=page, size=size)


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    return get_or_404(user_id)


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserIn):
    ensure_email_unique(payload.email)
    user = UserOut(id=next(id_seq), **payload.model_dump())
    users[user.id] = user
    return user


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserIn):
    get_or_404(user_id)
    ensure_email_unique(payload.email, exclude_id=user_id)
    users[user_id] = UserOut(id=user_id, **payload.model_dump())
    return users[user_id]


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    get_or_404(user_id)
    del users[user_id]
    return Response(status_code=204)
```

（共約 115 行）

## 3. 啟動與測試（Git Bash）

```bash
python -m pip install fastapi uvicorn pyjwt
export JWT_SECRET=$(python -c "import secrets;print(secrets.token_hex(32))") && uvicorn main:app &
TOKEN=$(python -c "import jwt,os;print(jwt.encode({'sub':'admin'},os.environ['JWT_SECRET'],algorithm='HS256'))") && curl -s -X POST localhost:8000/users -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"name":"Amy","email":"amy@example.com"}'
```

**注意事項：**
- **程式碼還沒實際跑過。** 這個環境沒有 shell 和寫檔工具，所以我沒有執行或測試它。建議用上面的指令驗證這幾種情況：不帶 token 應回 401、查不存在的 id 應回 404、email 重複應回 409、email 格式錯誤應回 422。
- **需要 Python 3.10 以上**，因為程式用了 `X | None` 這種型別寫法。
- **PUT 是整筆覆蓋。** 如果需要只改部分欄位，可以另外加一個 PATCH 端點，請求模型的欄位全設為 Optional，更新時用 `model_dump(exclude_unset=True)`。
- **資料存在記憶體 dict 裡。** 伺服器重啟資料就會消失，也不適合跑多個 worker。
