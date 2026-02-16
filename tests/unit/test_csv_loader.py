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
