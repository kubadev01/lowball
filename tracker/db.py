import sqlite3
from datetime import datetime
from pathlib import Path

from tracker.models import PriceInfo

SCHEMA = """
    CREATE TABLE IF NOT EXISTS games (
        app_id  TEXT PRIMARY KEY,
        name    TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS prices (
        id               INTEGER PRIMARY KEY,
        app_id           TEXT NOT NULL REFERENCES games(app_id),
        checked_at       TEXT NOT NULL,
        final            INTEGER NOT NULL,
        initial          INTEGER NOT NULL,
        discount_percent INTEGER NOT NULL,
        currency         TEXT NOT NULL
    );
"""


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def add_game(conn: sqlite3.Connection, app_id: str, name: str) -> None:
    with conn:
        conn.execute(
            "INSERT INTO games (app_id, name) VALUES (?, ?)",
            (app_id, name),
        )


def list_games(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    cursor = conn.execute("SELECT app_id, name FROM games ORDER BY name")
    return cursor.fetchall()


def record_price(
    conn: sqlite3.Connection, app_id: str, price: PriceInfo, checked_at: datetime
) -> None:
    with conn:
        conn.execute(
            """
                INSERT INTO prices 
                (app_id, checked_at, final, initial, discount_percent, currency) 
                VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                app_id,
                checked_at.isoformat(),
                price.final,
                price.initial,
                price.discount_percent,
                price.currency,
            ),
        )


def lowest_price(conn: sqlite3.Connection, app_id: str) -> int | None:
    cursor = conn.execute("SELECT MIN(final) FROM prices WHERE app_id = ?", (app_id,))
    (price,) = cursor.fetchone()
    return price
