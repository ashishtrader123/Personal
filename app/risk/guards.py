from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskGuards:
    starting_capital: float
    max_daily_loss_pct: float
    max_trades_per_day: int
    trades_today: int = 0
    realized_pnl: float = 0.0
    kill_switch: bool = False

    def can_trade(self) -> bool:
        if self.kill_switch:
            return False
        if self.trades_today >= self.max_trades_per_day:
            return False
        max_loss_amount = self.starting_capital * self.max_daily_loss_pct
        if self.realized_pnl <= -max_loss_amount:
            return False
        return True

    def register_trade(self, pnl: float) -> None:
        self.trades_today += 1
        self.realized_pnl += pnl

    def force_stop(self) -> None:
        self.kill_switch = True
