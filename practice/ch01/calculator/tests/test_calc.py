"""計算機測試：正常、邊界、錯誤三類案例。"""
import sys
from pathlib import Path

import pytest

# 讓測試從任何目錄執行都能 import 到 calculator/ 底下的模組
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import calculate, main  # noqa: E402
from utils import add, divide, multiply, subtract  # noqa: E402


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(10, 4) == 6


def test_multiply():
    assert multiply(3, 4) == 12


def test_divide():
    assert divide(10, 4) == 2.5


def test_negative_and_float():
    assert add(-1.5, 0.5) == -1.0
    assert multiply(-2, 0) == 0


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)


def test_calculate_unknown_operator():
    with pytest.raises(ValueError):
        calculate(1, "%", 2)


def test_main_cli(capsys):
    assert main(["3", "+", "4"]) == 0
    assert capsys.readouterr().out.strip() == "7.0"


def test_main_cli_bad_args():
    assert main(["3", "+"]) == 2
    assert main(["a", "+", "1"]) == 1
