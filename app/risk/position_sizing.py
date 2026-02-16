from __future__ import annotations


def calculate_quantity(capital: float, risk_per_trade_pct: float, entry: float, stop_loss: float) -> int:
    risk_amount = capital * risk_per_trade_pct
    per_unit_risk = abs(entry - stop_loss)
    if per_unit_risk <= 0:
        return 0
    qty = int(risk_amount // per_unit_risk)
    return max(qty, 0)
