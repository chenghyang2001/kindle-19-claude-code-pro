"""範例：有 bug 的平均分數計算（空清單會炸、None 分數會炸）"""


def average_score(scores):
    total = 0
    for s in scores:
        total += s
    return round(total / len(scores), 2)


if __name__ == "__main__":
    print(average_score([80, 90, 100]))
    print(average_score([]))
