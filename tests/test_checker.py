from datetime import UTC, datetime

import httpx

from tracker import checker, db
from tracker.models import PriceInfo
from tracker.stores.steam import GameNotFoundError

prices = {
    "001": PriceInfo(final=11999, initial=11999, discount_percent=0, currency="USD"),
    "002": PriceInfo(final=9999, initial=9999, discount_percent=0, currency="USD"),
    "003": None,
}


def fake_fetch(app_id: str) -> PriceInfo | None:
    if app_id == "404":
        raise GameNotFoundError(app_id)
    elif app_id == "500":
        raise httpx.ConnectError("boom")
    return prices[app_id]


def test_records_price_for_each_paid_game(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.add_game(conn, "002", "example2")

    result = checker.check_prices(conn, fake_fetch, datetime(2026, 11, 25, tzinfo=UTC))
    assert result.recorded == 2
    assert result.failed == []
    assert db.lowest_price(conn, "001") == 11999
    assert db.lowest_price(conn, "002") == 9999


def test_skips_free_games(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "003", "example3")
    result = checker.check_prices(conn, fake_fetch, datetime(2026, 11, 25, tzinfo=UTC))
    assert result.recorded == 0
    assert result.failed == []
    assert db.lowest_price(conn, "003") is None


def test_continues_after_failed_games(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.add_game(conn, "404", "example2")
    db.add_game(conn, "500", "example3")
    result = checker.check_prices(conn, fake_fetch, datetime(2026, 11, 25, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == ["404", "500"]
    assert db.lowest_price(conn, "001") == 11999
