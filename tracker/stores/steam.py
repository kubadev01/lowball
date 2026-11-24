import httpx

APPDETAILS_URL = "https://store.steampowered.com/api/appdetails"


def fetch_price(app_id: str) -> int | None:
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

    return game_data["price_overview"]["final"]


if __name__ == "__main__":
    for app_id in ["1091500", "570", "1"]:
        print(app_id, fetch_price(app_id))
