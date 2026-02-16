from __future__ import annotations

from collections import deque

from app.strategy.base import Strategy


class MomentumBreakoutStrategy(Strategy):
    def __init__(self, short_window: int = 5, long_window: int = 20) -> None:
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
        self.short_window = short_window
        self.long_window = long_window
        self._prices = deque(maxlen=long_window)
        self._last_signal = "HOLD"

    def on_price(self, price: float) -> str:
        self._prices.append(price)
        if len(self._prices) < self.long_window:
            return "HOLD"

        prices = list(self._prices)
        short_ma = sum(prices[-self.short_window :]) / self.short_window
        long_ma = sum(prices) / self.long_window

        signal = "HOLD"
        if short_ma > long_ma and self._last_signal != "BUY":
            signal = "BUY"
        elif short_ma < long_ma and self._last_signal != "SELL":
            signal = "SELL"

        if signal != "HOLD":
            self._last_signal = signal
        return signal
