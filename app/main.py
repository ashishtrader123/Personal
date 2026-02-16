from __future__ import annotations

from app.config.settings import load_settings
from app.data.market_stream import simulated_prices
from app.execution.paper_broker import PaperBroker
from app.risk.guards import RiskGuards
from app.risk.position_sizing import calculate_quantity
from app.strategy.momentum_breakout import MomentumBreakoutStrategy


def run() -> None:
    settings = load_settings()
    strategy = MomentumBreakoutStrategy(
        short_window=settings.short_window,
        long_window=settings.long_window,
    )
    broker = PaperBroker()
    guards = RiskGuards(
        starting_capital=settings.risk.capital,
        max_daily_loss_pct=settings.risk.max_daily_loss_pct,
        max_trades_per_day=settings.risk.max_trades_per_day,
    )

    print(f"Mode: {settings.mode} | Symbol: {settings.symbol}")
    for price in simulated_prices():
        signal = strategy.on_price(price)
        if signal == "HOLD":
            continue

        if not guards.can_trade():
            print("Risk guard active; trading stopped.")
            break

        stop = price * (0.997 if signal == "BUY" else 1.003)
        qty = calculate_quantity(
            capital=settings.risk.capital,
            risk_per_trade_pct=settings.risk.risk_per_trade_pct,
            entry=price,
            stop_loss=stop,
        )
        pnl = broker.place_market_order(signal=signal, qty=qty, price=price)
        guards.register_trade(pnl)
        print(
            f"price={price} signal={signal} qty={qty} trade_pnl={pnl:.2f} total_pnl={broker.realized_pnl:.2f}"
        )

    print(
        f"Session complete | Trades={guards.trades_today} | Realized PnL={broker.realized_pnl:.2f}"
    )


if __name__ == "__main__":
    run()
