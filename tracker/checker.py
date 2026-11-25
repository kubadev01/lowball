import sqlite3
from collections.abc import Callable
from datetime import datetime

from tracker import db
from tracker.models import PriceInfo

FetchPrice = Callable[[str], PriceInfo | None]


def check_prices(
    conn: sqlite3.Connection, fetch: FetchPrice, checked_at: datetime
) -> int:
    """Fetch the current price of every tracked game and store it.

    Returns the number of prices recorded.
    """
    recorded = 0
    for app_id, _ in db.list_games(conn):
        info = fetch(app_id)
        if info is None:
            continue
        db.record_price(conn, app_id, info, checked_at)
        recorded += 1

    return recorded
