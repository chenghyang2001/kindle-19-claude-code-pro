"""parse_date / process_data 測試：正常、邊界、錯誤、整合。"""
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from processor import load_csv, parse_date, process_data

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.mark.parametrize(
    "text",
    ["2024-01-15", "2024/01/15", "15-01-2024", "  2024-01-15  "],
)
def test_supported_formats(text):
    assert parse_date(text) == datetime(2024, 1, 15)


def test_original_failing_value_now_parses():
    # 就是 traceback 裡那個值
    assert parse_date("2024/01/15") == datetime(2024, 1, 15)


@pytest.mark.parametrize("bad", ["Jan 15 2024", "2024.01.15", "", "01-15-2024", "2024-02-30"])
def test_unparseable_returns_none_and_warns(bad, caplog):
    with caplog.at_level(logging.WARNING, logger="processor"):
        assert parse_date(bad) is None
    assert "無法解析日期" in caplog.text


@pytest.mark.parametrize("empty", [None, float("nan"), pd.NA])
def test_empty_values_return_none(empty, caplog):
    with caplog.at_level(logging.WARNING, logger="processor"):
        assert parse_date(empty) is None
    assert "空值" in caplog.text


def test_non_string_returns_none():
    assert parse_date(20240115) is None


def test_process_data_sample_csv_no_exception():
    result = process_data(load_csv(DATA_DIR / "sample.csv"))
    assert list(result) == [datetime(2024, 1, 14), datetime(2024, 1, 15), datetime(2024, 1, 16)]


def test_process_data_messy_csv_keeps_going():
    result = process_data(load_csv(DATA_DIR / "messy.csv")).tolist()
    assert result[:3] == [datetime(2024, 1, 14), datetime(2024, 1, 15), datetime(2024, 1, 16)]
    assert all(v is None or pd.isna(v) for v in result[3:])


def test_process_data_missing_column():
    with pytest.raises(KeyError):
        process_data(pd.DataFrame({"date": ["2024-01-15"]}))
