"""延伸思考：以 mock 隔離 DB 與通知服務，並斷言呼叫參數。"""
from unittest.mock import Mock

from starter.room_alert_service import check_room_and_notify


def make_repo(readings=None, error=None):
    repo = Mock()
    if error is not None:
        repo.fetch_readings.side_effect = error
    else:
        repo.fetch_readings.return_value = readings
    return repo


def test_sends_notification_with_room_and_level_when_level_is_unhealthy():
    # Arrange
    repo, notifier = make_repo([60, 60, 60, 60]), Mock()

    # Act
    result = check_room_and_notify(142, "2026-10-18", repo, notifier)

    # Assert
    repo.fetch_readings.assert_called_once_with(142, "2026-10-18")
    notifier.send.assert_called_once_with("場域 142 2026-10-18 PM2.5 60.0 → 不健康")
    assert result["notified"] is True


def test_does_not_notify_when_level_is_good():
    # Arrange
    repo, notifier = make_repo([5, 6, 7]), Mock()

    # Act
    result = check_room_and_notify(1, "2026-10-18", repo, notifier)

    # Assert
    notifier.send.assert_not_called()
    assert result["level"] == "良好"


def test_returns_query_failed_without_notifying_when_db_connection_fails():
    # Arrange
    repo, notifier = make_repo(error=ConnectionError("RDS timeout")), Mock()

    # Act
    result = check_room_and_notify(7, "2026-10-18", repo, notifier)

    # Assert
    assert result == {"room_id": 7, "level": "查詢失敗", "error": "RDS timeout", "notified": False}
    notifier.send.assert_not_called()


def test_does_not_notify_when_all_readings_are_fault_code():
    # Arrange
    repo, notifier = make_repo([998, 998]), Mock()

    # Act
    result = check_room_and_notify(9, "2026-10-18", repo, notifier)

    # Assert
    assert result["level"] == "資料不足"
    notifier.send.assert_not_called()
