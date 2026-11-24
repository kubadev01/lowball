import httpx
import pytest

from tracker.models import PriceInfo
from tracker.stores import steam


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
    monkeypatch.setattr(steam.httpx, "get", fake_get(200, body))

    result = steam.fetch_price("123")

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
    monkeypatch.setattr(steam.httpx, "get", fake_get(200, body))

    result = steam.fetch_price("123")

    assert result is None


def test_raises_for_unknown_game(monkeypatch):
    body = {
        "123": {
            "success": False,
        }
    }
    monkeypatch.setattr(steam.httpx, "get", fake_get(200, body))

    with pytest.raises(steam.GameNotFoundError):
        steam.fetch_price("123")


def test_raises_on_server_error(monkeypatch):
    monkeypatch.setattr(steam.httpx, "get", fake_get(500, {}))

    with pytest.raises(httpx.HTTPStatusError):
        steam.fetch_price("123")
