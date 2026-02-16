from app.risk.guards import RiskGuards


def test_risk_guards_stop_after_max_trades():
    guards = RiskGuards(starting_capital=300000, max_daily_loss_pct=0.02, max_trades_per_day=2)
    assert guards.can_trade()
    guards.register_trade(0)
    assert guards.can_trade()
    guards.register_trade(0)
    assert not guards.can_trade()
