from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class PriceBar:
    date: datetime
    close: float


def _parse_date(value: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def load_close_prices(csv_path: str) -> list[PriceBar]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    rows: list[PriceBar] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        lowered = {k.lower(): k for k in (reader.fieldnames or [])}
        if "date" not in lowered or "close" not in lowered:
            raise ValueError("CSV must have Date and Close columns")

        date_col = lowered["date"]
        close_col = lowered["close"]

        for row in reader:
            date = _parse_date(row[date_col])
            close = float(row[close_col])
            rows.append(PriceBar(date=date, close=close))

    rows.sort(key=lambda x: x.date)
    return rows


def last_n_days(prices: list[PriceBar], days: int = 30) -> list[PriceBar]:
    if not prices:
        return []
    end = prices[-1].date
    start = end - timedelta(days=days)
    return [bar for bar in prices if bar.date >= start]
