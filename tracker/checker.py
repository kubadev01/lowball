import sqlite3
from dataclasses import dataclass
from datetime import datetime

import httpx

from tracker import db
from tracker.stores.base import ProductNotFoundError, Store


@dataclass(frozen=True)
class CheckResult:
    recorded: int
    failed: list[str]
    new_lows: list[str]


def check_prices(
    conn: sqlite3.Connection, store: Store, checked_at: datetime
) -> CheckResult:
    """Fetch the current price of every tracked game and store it.

    Returns how many prices were recorded, which app IDs failed
    and which apps have a new lowest price.
    """
    recorded = 0
    failed = []
    new_lows = []
    for app_id, _ in db.list_games(conn):
        try:
            info = store.fetch_price(product_id=app_id)
        except (ProductNotFoundError, httpx.HTTPError):
            failed.append(app_id)
            continue
        if info is None:
            continue
        current_lowest_price = db.lowest_price(conn, app_id)
        if current_lowest_price is not None and info.final < current_lowest_price:
            new_lows.append(app_id)
        db.record_price(conn, app_id, info, checked_at)
        recorded += 1

    return CheckResult(recorded=recorded, failed=failed, new_lows=new_lows)
