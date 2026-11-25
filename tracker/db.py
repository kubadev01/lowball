import sqlite3
from pathlib import Path

SCHEMA = """
    CREATE TABLE IF NOT EXISTS games (
        app_id  TEXT PRIMARY KEY,
        name    TEXT NOT NULL
    );
"""


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
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
