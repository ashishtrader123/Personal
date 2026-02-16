from __future__ import annotations

from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def on_price(self, price: float) -> str:
        """Return BUY, SELL, or HOLD."""
