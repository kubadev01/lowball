import sqlite3

import pytest

from tracker import db


def test_added_game_is_listed(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "1091500", "Cyberpunk 2077")
    games = db.list_games(conn)
    assert games == [("1091500", "Cyberpunk 2077")]


def test_adding_same_game_twice_raises(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.add_game(conn, "1091500", "Cyberpunk2077")

    with pytest.raises(sqlite3.IntegrityError):
        db.add_game(conn, "1091500", "Cyberpunk2077")
