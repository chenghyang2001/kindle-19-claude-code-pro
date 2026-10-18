"""vulnerable/app.py 的修復版。

逐一對應修復：
  V1 SQL 注入        -> 一律參數化查詢（? 佔位符）
  V2 硬編碼密鑰      -> 從環境變數讀取，缺少即報錯
  V3 弱雜湊          -> PBKDF2-HMAC-SHA256 + 每人隨機 salt
  V4 命令注入        -> shell=False + 參數陣列 + 輸入白名單驗證
  V5 不安全反序列化  -> 改用 JSON，不再 pickle 不受信任資料
  V6 eval            -> 用 ast.literal_eval 只允許字面值
  V7 assert 權限檢查 -> 改成顯式 if + 擲例外
"""
import hashlib
import hmac
import ipaddress
import json
import os
import re
import subprocess
from ast import literal_eval

_PBKDF2_ROUNDS = 200_000


def _secret_key() -> bytes:
    """V2：密鑰只從環境變數取得，絕不寫死在程式碼。"""
    key = os.environ.get("APP_SECRET_KEY")
    if not key:
        raise RuntimeError("缺少環境變數 APP_SECRET_KEY")
    return key.encode()


def hash_password(password: str) -> str:
    """V3：PBKDF2 + 隨機 salt，輸出 `salt$hash`（皆為 hex）。"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """以常數時間比對驗證密碼。"""
    try:
        salt_hex, hash_hex = stored.split("$", 1)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), _PBKDF2_ROUNDS)
    return hmac.compare_digest(digest.hex(), hash_hex)


def init_db(conn) -> None:
    """建立示範資料表與兩位使用者。"""
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, pw_hash TEXT, role TEXT)")
    for uid, name, pw, role in [(1, "alice", "alice-pw", "admin"), (2, "bob", "bob-pw", "user")]:
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (uid, name, hash_password(pw), role))
    conn.commit()


def get_user(conn, user_id: int) -> list:
    """V1：參數化查詢，並強制 user_id 為整數。"""
    return conn.execute(
        "SELECT id, username, role FROM users WHERE id = ?", (int(user_id),)
    ).fetchall()


def login(conn, username: str, password: str):
    """V1 + V3：參數化查詢 + PBKDF2 驗證。"""
    row = conn.execute(
        "SELECT id, pw_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row and verify_password(password, row[1]):
        return issue_token(row[0])
    return None


def issue_token(user_id: int) -> str:
    """用環境變數密鑰簽 token。"""
    sig = hmac.new(_secret_key(), str(user_id).encode(), hashlib.sha256).hexdigest()
    return f"{user_id}.{sig}"


_HOSTNAME_RE = re.compile(r"^[A-Za-z0-9.-]{1,253}$")


def _is_valid_host(host: str) -> bool:
    """只接受合法 IP 或主機名，擋掉 shell 元字元。"""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return bool(_HOSTNAME_RE.fullmatch(host))


def ping_host(host: str) -> str:
    """V4：驗證輸入 + shell=False + 參數陣列，無法夾帶額外指令。"""
    if not _is_valid_host(host):
        raise ValueError(f"非法主機名：{host!r}")
    return subprocess.check_output(
        ["ping", "-n", "1", host], shell=False, text=True, errors="replace"
    )


def dump_session(data: dict) -> str:
    """V5：序列化改用 JSON。"""
    return json.dumps(data)


def load_session(blob: str) -> dict:
    """V5：JSON 反序列化不會執行任意程式碼。"""
    return json.loads(blob)


def calc(expression: str):
    """V6：literal_eval 只解析字面值，無法呼叫函式或 import。"""
    return literal_eval(expression)


def delete_user(conn, current_role: str, user_id: int) -> None:
    """V7：顯式權限檢查，不用 assert。"""
    if current_role != "admin":
        raise PermissionError("需要 admin 權限")
    conn.execute("DELETE FROM users WHERE id = ?", (int(user_id),))
    conn.commit()
