import httpx

from .enums import Bracket


def fetch_hero_stats() -> list:
    """Retrieves hero win/loss statistics from OpenDotaAPI."""
    r = httpx.get("https://api.opendota.com/api/heroStats")
    heroes = r.json()
    # Rename pro_<stat> to 8_<stat>, so it's easier to work with our enum
    for hero in heroes:
        for stat in ["win", "pick", "ban"]:
            hero[f"{Bracket.PRO.value}_{stat}"] = hero.pop(f"pro_{stat}")
    return heroes
