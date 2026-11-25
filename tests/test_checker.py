from datetime import UTC, datetime

from tracker import checker, db
from tracker.models import PriceInfo

prices = {
    "001": PriceInfo(final=11999, initial=11999, discount_percent=0, currency="USD"),
    "002": PriceInfo(final=9999, initial=9999, discount_percent=0, currency="USD"),
    "003": None,
}


def fake_fetch(app_id: str) -> PriceInfo | None:
    return prices[app_id]


def test_records_price_for_each_paid_game(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.add_game(conn, "002", "example2")

    recorded = checker.check_prices(
        conn, fake_fetch, datetime(2026, 11, 25, tzinfo=UTC)
    )
    assert recorded == 2
    assert db.lowest_price(conn, "001") == 11999
    assert db.lowest_price(conn, "002") == 9999


def test_skips_free_games(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "003", "example3")
    recorded = checker.check_prices(
        conn, fake_fetch, datetime(2026, 11, 25, tzinfo=UTC)
    )
    assert recorded == 0
    assert db.lowest_price(conn, "003") is None
