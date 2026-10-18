"""資料處理模組（修復版）：parse_date 支援多種日期格式。"""
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

# 依序嘗試。YYYY 開頭與 DD 開頭的格式靠「第一段是 4 位數還是 2 位數」自然區分，
# 不會互相誤判；但 DD-MM 與 MM-DD 無法區分，所以刻意不支援 MM-DD-YYYY。
SUPPORTED_FORMATS = (
    "%Y-%m-%d",  # 2024-01-15（原本支援）
    "%Y/%m/%d",  # 2024/01/15（Excel / 地區設定匯出常見）
    "%d-%m-%Y",  # 15-01-2024（預防性支援，歐洲慣例）
)


def parse_date(s):
    """把字串解析成 datetime；所有格式都失敗時 log 警告並回傳 None。"""
    if s is None or (not isinstance(s, str) and pd.isna(s)):
        logger.warning("parse_date 收到空值：%r", s)
        return None
    if not isinstance(s, str):
        logger.warning("parse_date 收到非字串：%r（型別 %s）", s, type(s).__name__)
        return None

    text = s.strip()
    for fmt in SUPPORTED_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    logger.warning("無法解析日期 %r，支援格式：%s", s, ", ".join(SUPPORTED_FORMATS))
    return None


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
    """把 timestamp 欄位轉成 datetime；解析失敗的值變成 None 而不是整批中斷。"""
    validate(df)
    return df["timestamp"].apply(parse_date)
