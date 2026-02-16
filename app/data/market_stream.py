from __future__ import annotations

import random
from typing import Iterator


def simulated_prices(start: float = 22000.0, steps: int = 100) -> Iterator[float]:
    price = start
    for _ in range(steps):
        price += random.uniform(-35, 35)
        yield round(price, 2)
