from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path

from app.data.csv_loader import _parse_date


@dataclass(frozen=True)
class OhlcBar:
    dt: datetime
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class DayResult:
    date: str
    signal: str
    strike: int | None
    entry_time: str | None
    exit_time: str | None
    exit_reason: str
    pnl: float


def load_ohlc_bars(csv_path: str) -> list[OhlcBar]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    bars: list[OhlcBar] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        reader = csv.DictReader(f, dialect=dialect)
        lowered = {k.lower(): k for k in (reader.fieldnames or [])}
        required = ("date", "open", "high", "low", "close")
        if any(col not in lowered for col in required):
            raise ValueError("CSV must include Date,Open,High,Low,Close headers")

        for row in reader:
            bars.append(
                OhlcBar(
                    dt=_parse_date(row[lowered["date"]]),
                    open=float(row[lowered["open"]]),
                    high=float(row[lowered["high"]]),
                    low=float(row[lowered["low"]]),
                    close=float(row[lowered["close"]]),
                )
            )

    bars.sort(key=lambda b: b.dt)
    return bars


def _nearest_100(price: float) -> int:
    return int(round(price / 100.0) * 100)


def run_backtest(
    bars: list[OhlcBar],
    lot_size: int = 75,
    reference_time: time = time(9, 0),
    stop_loss_pct: float = 0.30,
    target_pct: float = 0.70,
) -> list[DayResult]:
    by_day: dict[str, list[OhlcBar]] = {}
    for bar in bars:
        by_day.setdefault(bar.dt.date().isoformat(), []).append(bar)

    results: list[DayResult] = []

    for day, day_bars in by_day.items():
        day_bars.sort(key=lambda b: b.dt)

        ref = next((b for b in day_bars if b.dt.time() >= reference_time), None)
        if ref is None:
            results.append(DayResult(day, "NO_TRADE", None, None, None, "NO_REF_CANDLE", 0.0))
            continue

        ref_high, ref_low = ref.high, ref.low
        position = None
        entry_price = 0.0
        entry_time = None
        strike: int | None = None
        realized = 0.0
        exit_time = None
        exit_reason = "DAY_END"

        for bar in day_bars:
            if bar.dt <= ref.dt:
                continue

            if position is None:
                if bar.high > ref_high:
                    position = "BUY_CALL"
                    entry_price = bar.close
                    entry_time = bar.dt.strftime("%H:%M")
                    strike = _nearest_100(entry_price) + 100
                elif bar.low < ref_low:
                    position = "BUY_PUT"
                    entry_price = bar.close
                    entry_time = bar.dt.strftime("%H:%M")
                    strike = _nearest_100(entry_price) - 100
                else:
                    continue

            if position == "BUY_CALL":
                directional_points = bar.close - entry_price
                move_pct = (bar.close - entry_price) / entry_price
            else:
                directional_points = entry_price - bar.close
                move_pct = (entry_price - bar.close) / entry_price
            realized = directional_points * lot_size

            if move_pct <= -abs(stop_loss_pct):
                exit_time = bar.dt.strftime("%H:%M")
                exit_reason = "STOP_LOSS_PCT"
                break
            if move_pct >= abs(target_pct):
                exit_time = bar.dt.strftime("%H:%M")
                exit_reason = "TARGET_PCT"
                break

        if position is None:
            results.append(DayResult(day, "NO_TRADE", None, None, None, "NO_BREAKOUT", 0.0))
            continue

        if exit_time is None:
            last = day_bars[-1]
            exit_time = last.dt.strftime("%H:%M")
            if position == "BUY_CALL":
                realized = (last.close - entry_price) * lot_size
            else:
                realized = (entry_price - last.close) * lot_size

        results.append(
            DayResult(
                date=day,
                signal=position,
                strike=strike,
                entry_time=entry_time,
                exit_time=exit_time,
                exit_reason=exit_reason,
                pnl=round(realized, 2),
            )
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="9AM breakout analysis using BUY_CALL / BUY_PUT with 100-point strike offset"
    )
    parser.add_argument("--csv", required=True, help="CSV with Date,Open,High,Low,Close")
    parser.add_argument("--lot-size", type=int, default=75)
    parser.add_argument("--reference-hour", type=int, default=9)
    parser.add_argument("--reference-minute", type=int, default=0)
    parser.add_argument("--stop-loss-pct", type=float, default=0.30)
    parser.add_argument("--target-pct", type=float, default=0.70)
    args = parser.parse_args()

    bars = load_ohlc_bars(args.csv)
    results = run_backtest(
        bars,
        lot_size=args.lot_size,
        reference_time=time(args.reference_hour, args.reference_minute),
        stop_loss_pct=args.stop_loss_pct,
        target_pct=args.target_pct,
    )

    monthly = sum(r.pnl for r in results)
    print("Date       Signal     Strike Entry Exit  Reason          PnL")
    for r in results:
        strike = str(r.strike) if r.strike is not None else "-"
        print(
            f"{r.date} {r.signal:<10} {strike:>6} {str(r.entry_time or '-'):>5} {str(r.exit_time or '-'):>5} {r.exit_reason:<14} {r.pnl:>8.2f}"
        )
    print(f"\nTotal days: {len(results)}")
    print(f"Monthly PnL: {monthly:.2f}")


if __name__ == "__main__":
    main()
