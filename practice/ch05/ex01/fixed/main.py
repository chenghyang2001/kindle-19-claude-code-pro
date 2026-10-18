"""進入點：讀取 CSV 並處理 timestamp 欄位（修復版）。"""
import logging
import sys
from pathlib import Path

from processor import clean_columns, drop_empty_rows, load_csv, process_data, summarize

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample.csv"


def describe(df):
    info = summarize(df)
    print(f"讀到 {info['rows']} 筆，欄位：{info['columns']}")


if len(sys.argv) > 1:
    DATA_PATH = Path(sys.argv[1])

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
df = load_csv(DATA_PATH)
df = clean_columns(df)
df = drop_empty_rows(df)
describe(df)

result = process_data(df)
print(result)
