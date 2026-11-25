import sqlite3
from datetime import UTC, datetime

import pytest

from tracker import db
from tracker.models import PriceInfo


def test_added_game_is_listed(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "1091500", "Cyberpunk 2077")
    games = db.list_games(conn)
    assert games == [("1091500", "Cyberpunk 2077")]


def test_adding_same_game_twice_raises(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "1091500", "Cyberpunk 2077")

    with pytest.raises(sqlite3.IntegrityError):
        db.add_game(conn, "1091500", "Cyberpunk 2077")


def test_lowest_price_returns_minimum(tmp_path):
    conn = db.connect(tmp_path / "test.db")

    db.add_game(conn, "100", "Cyberpunk 2077")

    db.record_price(
        conn,
        "100",
        PriceInfo(final=120, initial=120, discount_percent=0, currency="USD"),
        datetime(2026, 11, 25, tzinfo=UTC),
    )

    db.record_price(
        conn,
        "100",
        PriceInfo(final=90, initial=90, discount_percent=0, currency="USD"),
        datetime(2026, 11, 25, tzinfo=UTC),
    )

    db.record_price(
        conn,
        "100",
        PriceInfo(final=140, initial=140, discount_percent=0, currency="USD"),
        datetime(2026, 11, 25, tzinfo=UTC),
    )

    minimum_price = db.lowest_price(conn, "100")
    assert minimum_price == 90


def test_lowest_price_is_none_without_records(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    minimum_price = db.lowest_price(conn, "101")
    assert minimum_price is None


def test_raises_for_unknown_game_price(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    with pytest.raises(sqlite3.IntegrityError):
        db.record_price(
            conn,
            "100",
            PriceInfo(final=140, initial=140, discount_percent=0, currency="USD"),
            datetime(2026, 11, 25, tzinfo=UTC),
        )
