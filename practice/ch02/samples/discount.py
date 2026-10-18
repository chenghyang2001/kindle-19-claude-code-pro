"""範例：同事寫的「需要改一下」的函式（可讀性差、魔術數字、重複邏輯）"""


def calc(p, t, q):
    if t == 1:
        if q > 10:
            r = p * q * 0.9
        else:
            r = p * q
    elif t == 2:
        if q > 10:
            r = p * q * 0.8
        else:
            r = p * q * 0.95
    else:
        r = p * q
    if r > 1000:
        r = r - 50
    return r
