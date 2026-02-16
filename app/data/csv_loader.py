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
    cleaned = value.strip()

    if " GMT" in cleaned:
        cleaned = cleaned.split(" GMT", maxsplit=1)[0].strip()

    for fmt in (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%a %b %d %Y %H:%M:%S",
    ):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def _load_from_header_rows(path: Path) -> list[PriceBar]:
    rows: list[PriceBar] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        reader = csv.DictReader(f, dialect=dialect)
        lowered = {k.lower(): k for k in (reader.fieldnames or [])}
        if "date" not in lowered or "close" not in lowered:
            return []

        date_col = lowered["date"]
        close_col = lowered["close"]
        for row in reader:
            date = _parse_date(row[date_col])
            close = float(row[close_col])
            rows.append(PriceBar(date=date, close=close))

    return rows


def _load_from_zerodha_ohlc_rows(path: Path) -> list[PriceBar]:
    rows: list[PriceBar] = []
    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            if "\t" in line:
                parts = [p.strip() for p in line.split("\t") if p.strip()]
            else:
                parts = [p.strip() for p in line.split(",") if p.strip()]

            if len(parts) < 5:
                continue

            date = _parse_date(parts[0])
            close = float(parts[4])
            rows.append(PriceBar(date=date, close=close))

    return rows


def load_close_prices(csv_path: str) -> list[PriceBar]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    rows = _load_from_header_rows(path)
    if not rows:
        rows = _load_from_zerodha_ohlc_rows(path)

    if not rows:
        raise ValueError(
            "Unsupported input format. Provide CSV with Date/Close headers or tab/comma rows in Date Open High Low Close format."
        )

    rows.sort(key=lambda x: x.date)
    return rows


def last_n_days(prices: list[PriceBar], days: int = 30) -> list[PriceBar]:
    if not prices:
        return []
    end = prices[-1].date
    start = end - timedelta(days=days)
    return [bar for bar in prices if bar.date >= start]
