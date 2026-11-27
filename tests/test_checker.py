from datetime import UTC, datetime

import httpx

from tracker import checker, db
from tracker.models import PriceInfo
from tracker.stores.base import ProductNotFoundError, Store

prices = {
    "001": PriceInfo(final=11999, initial=11999, discount_percent=0, currency="USD"),
    "002": PriceInfo(final=9999, initial=9999, discount_percent=0, currency="USD"),
    "003": None,
}


class FakeStore(Store):
    def fetch_price(self, product_id: str) -> PriceInfo | None:
        if product_id == "404":
            raise ProductNotFoundError(product_id)
        elif product_id == "500":
            raise httpx.ConnectError("boom")
        return prices[product_id]


def test_records_price_for_each_paid_game(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.add_game(conn, "002", "example2")
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 25, tzinfo=UTC))
    assert result.recorded == 2
    assert result.failed == []
    assert db.lowest_price(conn, "001") == 11999
    assert db.lowest_price(conn, "002") == 9999
    assert result.below_target == []
    assert result.new_lows == []


def test_skips_free_games(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "003", "example3")
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 25, tzinfo=UTC))
    assert result.recorded == 0
    assert result.failed == []
    assert db.lowest_price(conn, "003") is None
    assert result.below_target == []
    assert result.new_lows == []


def test_continues_after_failed_games(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.add_game(conn, "404", "example2")
    db.add_game(conn, "500", "example3")
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 25, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == ["404", "500"]
    assert db.lowest_price(conn, "001") == 11999
    assert result.below_target == []
    assert result.new_lows == []


def test_game_with_earlier_higher_price_in_new_lows(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.record_price(
        conn,
        "001",
        PriceInfo(final=14999, initial=14999, discount_percent=0, currency="USD"),
        datetime(2026, 11, 26, tzinfo=UTC),
    )
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == ["001"]
    assert result.below_target == []
    assert db.lowest_price(conn, "001") == 11999


def test_first_game_check_gives_not_new_low(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == []
    assert result.below_target == []
    assert db.lowest_price(conn, "001") == 11999


def test_game_price_is_current_minimum(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.record_price(
        conn,
        "001",
        PriceInfo(final=11999, initial=11999, discount_percent=0, currency="USD"),
        datetime(2026, 11, 26, tzinfo=UTC),
    )
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == []
    assert result.below_target == []
    assert db.lowest_price(conn, "001") == 11999


def test_price_below_the_target(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.set_target_price(conn, "001", 12000)
    db.record_price(
        conn,
        "001",
        PriceInfo(final=8999, initial=8999, discount_percent=0, currency="USD"),
        datetime(2026, 11, 26, tzinfo=UTC),
    )
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == []
    assert result.below_target == ["001"]
    assert db.lowest_price(conn, "001") == 8999


def test_price_is_the_target(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.set_target_price(conn, "001", 11999)
    db.record_price(
        conn,
        "001",
        PriceInfo(final=8999, initial=8999, discount_percent=0, currency="USD"),
        datetime(2026, 11, 26, tzinfo=UTC),
    )
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == []
    assert result.below_target == ["001"]
    assert db.lowest_price(conn, "001") == 8999


def test_price_above_the_target(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.set_target_price(conn, "001", 9999)
    db.record_price(
        conn,
        "001",
        PriceInfo(final=11999, initial=11999, discount_percent=0, currency="USD"),
        datetime(2026, 11, 26, tzinfo=UTC),
    )
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == []
    assert result.below_target == []
    assert db.lowest_price(conn, "001") == 11999


def test_first_check_below_target_is_reported(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.set_target_price(conn, "001", 12000)
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == []
    assert result.below_target == ["001"]
    assert db.lowest_price(conn, "001") == 11999


def test_price_back_above_target_is_not_reported(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "001", "example1")
    db.set_target_price(conn, "001", 10000)
    db.record_price(
        conn,
        "001",
        PriceInfo(final=9999, initial=9999, discount_percent=0, currency="USD"),
        datetime(2026, 11, 26, tzinfo=UTC),
    )
    fake_store = FakeStore()
    result = checker.check_prices(conn, fake_store, datetime(2026, 11, 27, tzinfo=UTC))
    assert result.recorded == 1
    assert result.failed == []
    assert result.new_lows == []
    assert result.below_target == []
    assert db.lowest_price(conn, "001") == 9999
