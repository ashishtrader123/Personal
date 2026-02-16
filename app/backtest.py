from __future__ import annotations

import argparse

from app.data.csv_loader import last_n_days, load_close_prices
from app.execution.paper_broker import PaperBroker
from app.risk.guards import RiskGuards
from app.risk.position_sizing import calculate_quantity
from app.strategy.momentum_breakout import MomentumBreakoutStrategy


def run_backtest(csv_path: str, capital: float = 300000.0) -> None:
    bars = load_close_prices(csv_path)
    month_bars = last_n_days(bars, days=30)
    if not month_bars:
        raise ValueError("No rows found in last 30 days of data")

    strategy = MomentumBreakoutStrategy(short_window=5, long_window=20)
    broker = PaperBroker()
    guards = RiskGuards(
        starting_capital=capital,
        max_daily_loss_pct=0.02,
        max_trades_per_day=1000,
    )

    for bar in month_bars:
        signal = strategy.on_price(bar.close)
        if signal == "HOLD" or not guards.can_trade():
            continue
        stop = bar.close * (0.997 if signal == "BUY" else 1.003)
        qty = calculate_quantity(
            capital=capital,
            risk_per_trade_pct=0.01,
            entry=bar.close,
            stop_loss=stop,
        )
        pnl = broker.place_market_order(signal=signal, qty=qty, price=bar.close)
        guards.register_trade(pnl)

    print(f"Rows processed (last 30 days): {len(month_bars)}")
    print(f"Trades executed: {guards.trades_today}")
    print(f"Realized PnL: {broker.realized_pnl:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backtest from CSV (Date,Close)")
    parser.add_argument("--csv", required=True, help="Path to CSV with Date,Close columns")
    parser.add_argument("--capital", type=float, default=300000.0)
    args = parser.parse_args()
    run_backtest(csv_path=args.csv, capital=args.capital)


if __name__ == "__main__":
    main()
