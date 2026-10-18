"""刻意有漏洞的使用者服務範例（教學用，切勿用於正式環境）。

內含漏洞：
  V1 SQL 注入            get_user / login 用 f-string 組 SQL
  V2 硬編碼密鑰          SECRET_KEY / DB_PASSWORD 寫死在程式碼（均為假值）
  V3 弱雜湊              密碼用 MD5、無 salt
  V4 命令注入            ping_host 用 shell=True 拼接使用者輸入
  V5 不安全反序列化      load_session 直接 pickle.loads 使用者資料
  V6 任意程式碼執行      calc 用 eval
  V7 用 assert 做權限檢查（python -O 時會被移除）
"""
import hashlib
import hmac
import pickle
import sqlite3
import subprocess

# V2：硬編碼密鑰（假值，僅供 bandit 偵測示範）
SECRET_KEY = "my-secret-key"
DB_PASSWORD = "P@ssw0rd-FAKE-123"


def init_db(conn: sqlite3.Connection) -> None:
    """建立示範資料表與兩位使用者。"""
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, pw_hash TEXT, role TEXT)")
    for uid, name, pw, role in [(1, "alice", "alice-pw", "admin"), (2, "bob", "bob-pw", "user")]:
        conn.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?)",
            (uid, name, hashlib.md5(pw.encode()).hexdigest(), role),  # V3
        )
    conn.commit()


def get_user(conn: sqlite3.Connection, user_id: str) -> list:
    """V1：直接把使用者輸入塞進 SQL。"""
    query = f"SELECT id, username, role FROM users WHERE id = {user_id}"
    return conn.execute(query).fetchall()


def login(conn: sqlite3.Connection, username: str, password: str):
    """V1 + V3：字串拼接 SQL + MD5 比對。"""
    pw_hash = hashlib.md5(password.encode()).hexdigest()
    query = "SELECT id, username FROM users WHERE username = '" + username + "' AND pw_hash = '" + pw_hash + "'"
    row = conn.execute(query).fetchone()
    if row:
        return issue_token(row[0])
    return None


def issue_token(user_id: int) -> str:
    """用硬編碼密鑰簽 token。"""
    sig = hmac.new(SECRET_KEY.encode(), str(user_id).encode(), hashlib.sha256).hexdigest()
    return f"{user_id}.{sig}"


def ping_host(host: str) -> str:
    """V4：shell=True 拼接，host 可夾帶 `& 其他指令`。"""
    return subprocess.check_output(f"ping -n 1 {host}", shell=True, text=True, errors="replace")


def load_session(blob: bytes):
    """V5：反序列化不受信任的資料。"""
    return pickle.loads(blob)


def calc(expression: str):
    """V6：eval 使用者輸入。"""
    return eval(expression)


def delete_user(conn: sqlite3.Connection, current_role: str, user_id: int) -> None:
    """V7：assert 在最佳化模式會被移除，權限檢查失效。"""
    assert current_role == "admin", "需要 admin 權限"
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
