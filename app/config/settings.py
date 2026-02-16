from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    capital: float = 300000.0
    risk_per_trade_pct: float = 0.01
    max_daily_loss_pct: float = 0.02
    max_trades_per_day: int = 5


@dataclass(frozen=True)
class AppSettings:
    symbol: str = "NSE:NIFTY 50"
    short_window: int = 5
    long_window: int = 20
    bar_interval_minutes: int = 5
    mode: str = "paper"
    risk: RiskConfig = RiskConfig()



def load_settings() -> AppSettings:
    capital = float(os.getenv("CAPITAL", "300000"))
    risk_pct = float(os.getenv("RISK_PER_TRADE_PCT", "0.01"))
    max_loss_pct = float(os.getenv("MAX_DAILY_LOSS_PCT", "0.02"))
    max_trades = int(os.getenv("MAX_TRADES_PER_DAY", "5"))

    return AppSettings(
        symbol=os.getenv("SYMBOL", "NSE:NIFTY 50"),
        short_window=int(os.getenv("SHORT_WINDOW", "5")),
        long_window=int(os.getenv("LONG_WINDOW", "20")),
        bar_interval_minutes=int(os.getenv("BAR_INTERVAL_MINUTES", "5")),
        mode=os.getenv("MODE", "paper"),
        risk=RiskConfig(
            capital=capital,
            risk_per_trade_pct=risk_pct,
            max_daily_loss_pct=max_loss_pct,
            max_trades_per_day=max_trades,
        ),
    )
