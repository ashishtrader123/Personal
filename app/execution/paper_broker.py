from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position:
    side: str
    qty: int
    entry_price: float


class PaperBroker:
    def __init__(self) -> None:
        self.position: Position | None = None
        self.realized_pnl = 0.0

    def place_market_order(self, signal: str, qty: int, price: float) -> float:
        if qty <= 0:
            return 0.0

        if signal == "BUY":
            if self.position and self.position.side == "SELL":
                pnl = (self.position.entry_price - price) * self.position.qty
                self.realized_pnl += pnl
                self.position = None
                return pnl
            if self.position is None:
                self.position = Position(side="BUY", qty=qty, entry_price=price)
            return 0.0

        if signal == "SELL":
            if self.position and self.position.side == "BUY":
                pnl = (price - self.position.entry_price) * self.position.qty
                self.realized_pnl += pnl
                self.position = None
                return pnl
            if self.position is None:
                self.position = Position(side="SELL", qty=qty, entry_price=price)
            return 0.0

        return 0.0
