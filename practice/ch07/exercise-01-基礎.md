# 練習 01 — 基礎：識別程式碼異味

## 情境說明
你接手一個「運作中但沒人敢碰」的 Python 函式，需要先分析問題再動手重構。

## 目標程式碼（需要分析）

```python
def process(d, t, r=True):
    result = []
    if d:
        for i in range(len(d)):
            if d[i] != None:
                if t == "pm25":
                    if d[i] >= 0 and d[i] <= 500:
                        if d[i] != 998:
                            result.append(d[i])
                        else:
                            pass
                    else:
                        pass
                elif t == "temp":
                    if d[i] >= -40 and d[i] <= 85:
                        result.append(d[i])
                else:
                    result.append(d[i])
    if r == True:
        if len(result) > 0:
            total = 0
            for x in result:
                total = total + x
            avg = total / len(result)
            return round(avg, 2)
        else:
            return 0
    else:
        return result
```

## 任務

### 任務 1：異味掃描
列出所有你發現的程式碼異味，使用以下分類：

| 異味類型 | 具體問題 | 影響程度（高/中/低）|
|---------|---------|----------------|
| 命名含糊 | 函式名稱 `process` 沒說明做什麼 | 高 |
| ... | ... | ... |

至少找出 5 個不同的問題。

### 任務 2：優先排序
對找到的異味依「重構後獲益」排序：
1. 最值得先做的是哪個？為什麼？
2. 哪個最簡單可以快速解決？
3. 哪個最危險（動錯了最容易引入 bug）？

## 完成後
將異味清單 + 優先排序存入 `answer/ex01-answer.md`
