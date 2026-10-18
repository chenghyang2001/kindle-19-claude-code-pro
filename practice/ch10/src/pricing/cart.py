"""購物車計價：小計、折扣、稅金。"""

from decimal import ROUND_HALF_UP, Decimal

TAX_RATE = Decimal("0.05")  # 台灣營業稅 5%


def subtotal(items: list[tuple[str, Decimal, int]]) -> Decimal:
    """計算小計。items 每筆為 (品名, 單價, 數量)。"""
    total = Decimal("0")
    for name, price, qty in items:
        if price < 0 or qty < 0:
            raise ValueError(f"品項 {name!r} 的單價或數量不可為負數")
        total += price * qty
    return total


def apply_discount(amount: Decimal, percent: int) -> Decimal:
    """套用百分比折扣，percent 必須在 0~100。"""
    if not 0 <= percent <= 100:
        raise ValueError(f"折扣百分比必須在 0~100，收到 {percent}")
    return amount * (Decimal(100 - percent) / Decimal(100))


def total_with_tax(amount: Decimal) -> Decimal:
    """加上營業稅並四捨五入到整數元。"""
    return (amount * (1 + TAX_RATE)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
