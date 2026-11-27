import httpx
import pytest

from tracker.models import PriceInfo
from tracker.stores import steam
from tracker.stores.base import ProductNotFoundError, Store


def fake_get(status_code, json_body):
    def _get(url, params, timeout):
        request = httpx.Request("GET", url, params=params)
        return httpx.Response(status_code, json=json_body, request=request)

    return _get


def test_returns_price_info_for_paid_game(monkeypatch):
    body = {
        "123": {
            "success": True,
            "data": {
                "price_overview": {
                    "final": 4999,
                    "initial": 9999,
                    "discount_percent": 50,
                    "currency": "PLN",
                }
            },
        }
    }

    store = steam.SteamStore()
    monkeypatch.setattr(steam.httpx, "get", fake_get(200, body))

    result = store.fetch_price("123")

    assert result == PriceInfo(
        final=4999, initial=9999, discount_percent=50, currency="PLN"
    )


def test_returns_none_for_free_game(monkeypatch):
    body = {
        "123": {
            "success": True,
            "data": [],
        }
    }

    store = steam.SteamStore()
    monkeypatch.setattr(steam.httpx, "get", fake_get(200, body))

    result = store.fetch_price("123")

    assert result is None


def test_raises_for_unknown_game(monkeypatch):
    body = {
        "123": {
            "success": False,
        }
    }

    store = steam.SteamStore()
    monkeypatch.setattr(steam.httpx, "get", fake_get(200, body))

    with pytest.raises(steam.GameNotFoundError):
        store.fetch_price("123")


def test_raises_on_server_error(monkeypatch):
    store = steam.SteamStore()
    monkeypatch.setattr(steam.httpx, "get", fake_get(500, {}))

    with pytest.raises(httpx.HTTPStatusError):
        store.fetch_price("123")


def test_steam_store_is_a_store():
    store = steam.SteamStore()
    assert isinstance(store, Store)


def test_unknown_game_is_product_not_found(monkeypatch):
    body = {
        "123": {
            "success": False,
        }
    }

    store = steam.SteamStore()
    monkeypatch.setattr(steam.httpx, "get", fake_get(200, body))

    with pytest.raises(ProductNotFoundError):
        store.fetch_price("123")
