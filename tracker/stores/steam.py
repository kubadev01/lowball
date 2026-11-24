import httpx

from tracker.models import PriceInfo

APPDETAILS_URL = "https://store.steampowered.com/api/appdetails"


def fetch_price(app_id: str) -> PriceInfo | None:
    response = httpx.get(
        APPDETAILS_URL,
        params={"appids": app_id, "cc": "pl", "filters": "price_overview"},
        timeout=10.0,
    )

    response.raise_for_status()

    game = response.json()[app_id]
    if not game["success"]:
        return None

    game_data = game["data"]
    if not game_data:
        return None

    overview = game_data["price_overview"]
    return PriceInfo(
        final=overview["final"],
        initial=overview["initial"],
        discount_percent=overview["discount_percent"],
        currency=overview["currency"],
    )


if __name__ == "__main__":
    for app_id in ["1091500", "570", "1"]:
        try:
            print(app_id, fetch_price(app_id))
        except httpx.HTTPError as error:
            print(f"{app_id}: network error ({error})")
