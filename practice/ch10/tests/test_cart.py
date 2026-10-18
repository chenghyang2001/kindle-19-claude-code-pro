"""cart 模組測試：正常、邊界、錯誤三類案例。"""

from decimal import Decimal

import pytest

from pricing.cart import apply_discount, subtotal, total_with_tax


def test_subtotal_normal():
    items = [("筆", Decimal("30"), 2), ("本子", Decimal("45"), 1)]
    assert subtotal(items) == Decimal("105")


def test_subtotal_empty():
    assert subtotal([]) == Decimal("0")


def test_subtotal_negative_raises():
    with pytest.raises(ValueError):
        subtotal([("壞資料", Decimal("-1"), 1)])


@pytest.mark.parametrize(("percent", "expected"), [(0, "200"), (25, "150"), (100, "0")])
def test_apply_discount(percent, expected):
    assert apply_discount(Decimal("200"), percent) == Decimal(expected)


def test_apply_discount_out_of_range():
    with pytest.raises(ValueError):
        apply_discount(Decimal("100"), 101)


def test_total_with_tax_rounding():
    assert total_with_tax(Decimal("105")) == Decimal("110")  # 110.25 → 110
    assert total_with_tax(Decimal("110")) == Decimal("116")  # 115.5 → 116（四捨五入）
