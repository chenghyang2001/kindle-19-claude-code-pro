"""延伸思考示範：依賴外部服務（DB + 通知）的函式，用依賴注入讓測試可以 mock。"""
from typing import Protocol

from starter.alert_level import classify_alert_level

NOTIFY_LEVELS = {"不健康", "非常不健康", "危害"}


class ReadingRepository(Protocol):
    def fetch_readings(self, room_id: int, date: str) -> list[float]: ...


class Notifier(Protocol):
    def send(self, message: str) -> None: ...


def check_room_and_notify(room_id: int, date: str, repo: ReadingRepository, notifier: Notifier) -> dict:
    """查詢場域讀數、判定等級；達「不健康」以上才發通知。DB 失敗時回傳錯誤狀態，不發通知。"""
    try:
        readings = repo.fetch_readings(room_id, date)
    except ConnectionError as exc:
        return {"room_id": room_id, "level": "查詢失敗", "error": str(exc), "notified": False}

    result = classify_alert_level(readings)
    should_notify = result["level"] in NOTIFY_LEVELS
    if should_notify:
        notifier.send(f"場域 {room_id} {date} PM2.5 {result['avg']} → {result['level']}")
    return {"room_id": room_id, **result, "notified": should_notify}
