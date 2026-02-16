from __future__ import annotations

from datetime import datetime

from app.analysis.ten_am_breakout import OhlcBar, run_backtest


def test_stop_loss_for_sell_call_breakdown() -> None:
    bars = [
        OhlcBar(datetime(2026, 2, 16, 10, 0), 100, 110, 95, 100),
        OhlcBar(datetime(2026, 2, 16, 10, 1), 100, 102, 94, 95),  # breakout below low
        OhlcBar(datetime(2026, 2, 16, 10, 2), 95, 130, 95, 130),  # adverse move
    ]

    results = run_backtest(bars, lot_size=75, daily_stop_loss=2000, daily_target=4000)

    assert len(results) == 1
    assert results[0].signal == "SELL_CALL"
    assert results[0].exit_reason == "STOP_LOSS"
    assert results[0].pnl == -2625.0


def test_target_for_sell_put_breakout_up() -> None:
    bars = [
        OhlcBar(datetime(2026, 2, 17, 10, 0), 100, 105, 95, 100),
        OhlcBar(datetime(2026, 2, 17, 10, 1), 100, 106, 99, 102),  # breakout above high
        OhlcBar(datetime(2026, 2, 17, 10, 2), 102, 170, 101, 170),
    ]

    results = run_backtest(bars, lot_size=75, daily_stop_loss=2000, daily_target=4000)

    assert len(results) == 1
    assert results[0].signal == "SELL_PUT"
    assert results[0].exit_reason == "TARGET"
    assert results[0].pnl == 5100.0
