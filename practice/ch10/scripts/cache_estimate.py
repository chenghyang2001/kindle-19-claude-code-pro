"""pip 快取時間估算（練習 01 任務 2）。"""


def estimate(packages: int, seconds_each: float, restore_seconds: float = 0.0) -> dict:
    """回傳首次、快取命中時的安裝秒數與節省秒數。restore_seconds 是還原快取本身的開銷。"""
    if packages < 0 or seconds_each < 0 or restore_seconds < 0:
        raise ValueError("套件數與秒數不可為負")
    first = packages * seconds_each
    return {"first_run": first, "cached_run": restore_seconds, "saved": first - restore_seconds}


if __name__ == "__main__":
    ideal = estimate(10, 2)
    realistic = estimate(10, 2, restore_seconds=3)
    print(f"理想模型：首次 {ideal['first_run']:.0f} 秒，命中後節省 {ideal['saved']:.0f} 秒")
    print(
        f"含還原開銷 3 秒：命中後約 {realistic['cached_run']:.0f} 秒，"
        f"節省 {realistic['saved']:.0f} 秒"
    )
    print(f"3 個 job 各裝一次，每次 push 理想共省 {ideal['saved'] * 3:.0f} 秒")
