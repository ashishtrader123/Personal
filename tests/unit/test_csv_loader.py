from pathlib import Path

from app.data.csv_loader import last_n_days, load_close_prices


def test_load_close_prices_and_filter_last_n_days(tmp_path: Path):
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "Date,Close\n2026-01-01,100\n2026-01-20,110\n2026-02-10,115\n",
        encoding="utf-8",
    )

    rows = load_close_prices(str(csv_path))
    assert len(rows) == 3

    month_rows = last_n_days(rows, days=30)
    assert len(month_rows) == 2
    assert month_rows[0].close == 110.0


def test_load_zerodha_style_ohlc_rows(tmp_path: Path):
    csv_path = tmp_path / "zerodha_rows.txt"
    csv_path.write_text(
        "Wed Nov 26 2025 00:00:00 GMT+0530 (India Standard Time)\t26280.8\t26694.8\t26280.8\t26676.9\n"
        "Thu Nov 27 2025 00:00:00 GMT+0530 (India Standard Time)\t26699\t26791.2\t26630.5\t26699.1\n",
        encoding="utf-8",
    )

    rows = load_close_prices(str(csv_path))
    assert len(rows) == 2
    assert rows[0].close == 26676.9
    assert rows[1].close == 26699.1
