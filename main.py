import sys
from enum import Enum
from typing import List
from pathlib import Path

import requests

from config import Config


class Brackets(Enum):
    HERALD = 1
    GUARDIAN = 2
    CRUSADER = 3
    ARCHON = 4
    LEGEND = 5
    ANCIENT = 6
    DIVINE = 7


DOTA_GRID = {
    "version": 3,
    "configs": [
        {
            "config_name": "Opendota Hero Winrate",
            "categories": [
                {
                    "category_name": "Heroes Sorted By Winrate",
                    "x_position": 0.000000,
                    "y_position": 0.000000,
                    "width": 900.0,
                    "height": 500.0,
                    "hero_ids": [],
                }
            ],
        }
    ],
}


def get_hero_stats(bracket: int) -> List[int]:
    r = requests.get("https://api.opendota.com/api/heroStats")

    heroes = r.json()
    heroes.sort(key=lambda h: h[f"{bracket}_pick"] / h[f"{bracket}_win"])

    return [hero["id"] for hero in heroes]


def format_hero_grid(heroes: List[int]) -> dict:
    d = DOTA_GRID.copy()
    d["configs"][0]["categories"][0]["ids"].extend(heroes)

def get_default_cfg_path():
    d = f"Steam/userdata/{Config.USER_ID}/570/remote/cfg"
    if sys.platform == "win32":
        p = Path(f"C:/Program Files(x86)") / d
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support" / d
    elif sys.platform == "linux":
        p = Path.home() / d
    else:
        raise NotImplementedError("Your OS is not supported! Try to supply directory path manually.")

if __name__ == "__main__":    
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        bracket = sys.argv[1]
    else:
        bracket = Config.DEFAULT_BRACKET

    try:
        cfg_path = sys.argv[2]
    except IndexError:
        cfg_path = get_default_cfg_path()

    heroes = get_hero_stats(bracket)
