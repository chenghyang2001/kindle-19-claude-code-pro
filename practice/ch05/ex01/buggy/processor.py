"""資料處理模組（同事留下的有 bug 版本）。

刻意保留原始寫法，用來重現練習題中的 stack trace。
"""
from datetime import datetime

import pandas as pd


def parse_date(s):
    # 原作者假設所有日期都是 ISO 格式（YYYY-MM-DD）
    return datetime.strptime(s, "%Y-%m-%d")


def load_csv(path):
    """讀取 CSV，所有欄位先當字串讀，避免 pandas 自作主張轉型。"""
    return pd.read_csv(path, dtype=str)


def clean_columns(df):
    """欄位名稱去空白、轉小寫。"""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def drop_empty_rows(df):
    """移除整列都是空值的資料。"""
    return df.dropna(how="all")


def summarize(df):
    """回傳筆數與欄位清單，方便 debug 時印出。"""
    return {"rows": len(df), "columns": list(df.columns)}


def validate(df):
    """確認必要欄位存在。"""
    if "timestamp" not in df.columns:
        raise KeyError("缺少 timestamp 欄位")


def process_data(df):
    validate(df)
    return df["timestamp"].apply(parse_date)
