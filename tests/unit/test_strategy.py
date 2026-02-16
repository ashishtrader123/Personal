from app.strategy.momentum_breakout import MomentumBreakoutStrategy


def test_strategy_generates_signal_after_window():
    strategy = MomentumBreakoutStrategy(short_window=3, long_window=5)
    prices = [100, 101, 102, 103, 104, 105]
    signals = [strategy.on_price(p) for p in prices]
    assert any(sig in {"BUY", "SELL"} for sig in signals)
