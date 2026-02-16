from app.risk.position_sizing import calculate_quantity


def test_position_sizing_positive_qty():
    qty = calculate_quantity(capital=300000, risk_per_trade_pct=0.01, entry=100, stop_loss=99)
    assert qty == 3000
