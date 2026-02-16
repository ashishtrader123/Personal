from __future__ import annotations

from datetime import datetime, time

from app.analysis.ten_am_breakout import OhlcBar, run_backtest


def test_buy_put_day_end_after_9am_bearish_breakout() -> None:
    bars = [
        OhlcBar(datetime(2026, 2, 16, 9, 0), 100, 110, 95, 100),
        OhlcBar(datetime(2026, 2, 16, 9, 1), 100, 102, 94, 95),
        OhlcBar(datetime(2026, 2, 16, 9, 2), 95, 96, 92, 93),
    ]

    results = run_backtest(
        bars,
        lot_size=75,
        reference_time=time(9, 0),
        stop_loss_pct=0.30,
        target_pct=0.70,
    )

    assert len(results) == 1
    assert results[0].signal == "BUY_PUT"
    assert results[0].exit_reason == "DAY_END"
    assert results[0].pnl == 150.0


def test_stop_loss_pct_for_buy_call_breakout_up() -> None:
    bars = [
        OhlcBar(datetime(2026, 2, 17, 9, 0), 100, 105, 95, 100),
        OhlcBar(datetime(2026, 2, 17, 9, 1), 100, 106, 99, 100),
        OhlcBar(datetime(2026, 2, 17, 9, 2), 100, 101, 60, 60),
    ]

    results = run_backtest(
        bars,
        lot_size=75,
        reference_time=time(9, 0),
        stop_loss_pct=0.30,
        target_pct=0.70,
    )

    assert len(results) == 1
    assert results[0].signal == "BUY_CALL"
    assert results[0].exit_reason == "STOP_LOSS_PCT"
    assert results[0].pnl == -3000.0
