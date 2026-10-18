"""練習 02 審查對象：一個「看起來能跑」的訂單報表函式（刻意含缺陷，勿修改）。"""
import sqlite3
import requests

API_KEY = "sk-demo-not-a-real-key"
DB = "C:/Users/demo/shop.db"


def send_order_report(customer):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"SELECT id, amount FROM orders WHERE customer = '{customer}'")
    rows = cur.fetchall()
    total = 0
    for r in rows:
        total = total + r[1]
    avg = total / len(rows)
    d = {"customer": customer, "count": len(rows), "total": total, "avg": avg}
    try:
        res = requests.post(
            "https://report.example.com/api",
            json=d,
            headers={"Authorization": "Bearer " + API_KEY},
        )
    except:
        pass
    print("sent", d)
    return d
