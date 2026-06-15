import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import add, subtract, multiply, divide

def test_add():    assert add(2, 3) == 5
def test_sub():    assert subtract(5, 3) == 2
def test_mul():    assert multiply(4, 3) == 12
def test_div():    assert divide(10, 2) == 5.0
def test_div_zero():
    try: divide(1, 0)
    except ValueError: pass

if __name__ == "__main__":
    test_add(); test_sub(); test_mul(); test_div(); test_div_zero()
    print("所有測試通過！")
