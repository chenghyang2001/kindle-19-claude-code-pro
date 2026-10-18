"""計算機命令列入口：python main.py 3 + 4"""
import sys

from utils import add, divide, multiply, subtract

OPERATIONS = {"+": add, "-": subtract, "*": multiply, "/": divide}


def calculate(a, op, b):
    if op not in OPERATIONS:
        raise ValueError(f"不支援的運算子：{op}（可用 + - * /）")
    return OPERATIONS[op](a, b)


def main(argv):
    if len(argv) != 3:
        print("用法：python main.py <數字> <+|-|*|/> <數字>", file=sys.stderr)
        return 2
    try:
        a, op, b = float(argv[0]), argv[1], float(argv[2])
        print(calculate(a, op, b))
        return 0
    except ValueError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
