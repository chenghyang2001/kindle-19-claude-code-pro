"""練習 01：用可執行範例重現 5 種「AI 生成程式碼」特有風險（全部無害、離線可跑）。

執行：PYTHONUTF8=1 .venv/Scripts/python answer/demo/ex01_ai_risk_demo.py
"""
import hashlib
import importlib.util
import os
import random
import secrets
import subprocess
import sys
import time


def risk1_hallucinated_api() -> None:
    """幻覺 API：AI 常「發明」看似合理的函式名稱。"""
    print("[風險1] 幻覺 API 檢查")
    claims = [("hashlib", "secureHash"), ("hashlib", "pbkdf2_hmac"), ("secrets", "token_urlsafe"), ("secrets", "secure_random_string")]
    for module_name, attr in claims:
        mod = __import__(module_name)
        print(f"  {module_name}.{attr:22} 存在? {hasattr(mod, attr)}")
    for pkg in ["requests_secure_auth", "json"]:
        print(f"  套件 {pkg:22} 可匯入? {importlib.util.find_spec(pkg) is not None}")
    print("  -> 不存在的名稱若被開發者「自己補一個」或被搶註成惡意套件（slopsquatting），就成了漏洞")


def risk2_outdated_advice() -> None:
    """過時建議：舊教材常見「MD5 存密碼」。比較每秒可試次數。"""
    print("[風險2] 過時安全建議：MD5 vs PBKDF2（200k 輪）")
    n = 200_000
    start = time.perf_counter()
    for i in range(n):
        hashlib.md5(str(i).encode()).digest()
    md5_rate = n / (time.perf_counter() - start)
    start = time.perf_counter()
    hashlib.pbkdf2_hmac("sha256", b"pw", b"salt0123456789ab", 200_000)
    pbkdf2_rate = 1 / (time.perf_counter() - start)
    print(f"  單核 MD5 每秒 {md5_rate:,.0f} 次；PBKDF2 每秒 {pbkdf2_rate:,.1f} 次；差 {md5_rate / pbkdf2_rate:,.0f} 倍")
    print("  -> 依舊建議寫的雜湊，離線暴力破解成本極低")


def risk3_generic_code() -> None:
    """過度通用：AI 預設 Linux 環境，指令在 Windows 上行為不同。"""
    print(f"[風險3] 過度通用：在 {sys.platform} 執行 Linux 慣用的 `ping -c 1 127.0.0.1`")
    try:
        result = subprocess.run(["ping", "-c", "1", "127.0.0.1"], capture_output=True, timeout=15)
        print(f"  exit code = {result.returncode}（Windows 的 ping 沒有 -c 選項，含意不同）")
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"  執行失敗：{type(exc).__name__}")
    temp_dir = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"
    print(f"  AI 常寫死 /tmp；本機暫存目錄是 /tmp 嗎? {temp_dir == '/tmp'}（Windows 為 %TEMP%）")
    print("  -> 錯誤路徑/權限/選項，可能讓暫存檔落到他人可讀位置，或讓驗證邏輯靜默失效")


def ai_style_checkout(price: int, qty: int, coupon_pct: int) -> int:
    """AI 典型產出：語法正確、型別正確，卻沒有業務規則。"""
    return price * qty * (100 - coupon_pct) // 100


def risk4_missing_business_rules() -> None:
    """缺少業務邏輯驗證：數量與折扣沒有範圍限制。"""
    print("[風險4] 缺少業務邏輯驗證")
    print(f"  qty=-3            -> 總價 {ai_style_checkout(1000, -3, 0)}（變成退款）")
    print(f"  coupon_pct=150    -> 總價 {ai_style_checkout(1000, 1, 150)}（倒貼）")
    print("  -> 只有你知道「數量 1~99、折扣上限 30%、一人一張券」這些規則")


def risk5_blind_trust() -> None:
    """過度信任：複製貼上用 random 產生重設密碼 token。"""
    print("[風險5] 過度信任 AI 輸出：random 產生的 token 可被預測")
    random.seed(1234)  # 攻擊者若猜到種子（如啟動時間）
    victim_token = "".join(random.choices("0123456789abcdef", k=16))
    random.seed(1234)
    attacker_guess = "".join(random.choices("0123456789abcdef", k=16))
    print(f"  受害者 token {victim_token} / 攻擊者重算 {attacker_guess} / 相同 {victim_token == attacker_guess}")
    print(f"  正確作法 secrets.token_hex(8) -> {secrets.token_hex(8)}")


def main() -> None:
    try:
        for step in [risk1_hallucinated_api, risk2_outdated_advice, risk3_generic_code, risk4_missing_business_rules, risk5_blind_trust]:
            step()
            print()
    except Exception as exc:  # 示範腳本：任何錯誤都印出後以非 0 結束
        print(f"錯誤：{exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
