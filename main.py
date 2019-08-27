import sys
import json
from enum import Enum
from typing import List
from pathlib import Path

import requests
import click

from config import Config
from resources import DOTA_GRID


class Brackets(Enum):
    HERALD = 1
    GUARDIAN = 2
    CRUSADER = 3
    ARCHON = 4
    LEGEND = 5
    ANCIENT = 6
    DIVINE = 7
    PRO = "pro"


DEFAULT_BRACKET = Brackets.DIVINE.value


def get_hero_stats() -> list:
    """Retrieves hero win/loss statistics from OpenDotaAPI."""
    r = requests.get("https://api.opendota.com/api/heroStats")
    heroes = r.json()
    return heroes


def sort_heroes_by_winrate(heroes: list, bracket: str) -> list:
    """Sorts list of heroes by winrate in a specific skill bracket."""
    heroes.sort(key=lambda h: h[f"{bracket}_pick"] / h[f"{bracket}_win"])
    return heroes
    

def format_hero_grid(heroes: List[int]) -> dict:
    d = DOTA_GRID.copy()
    indexes = {
        "str": 0,
        "agi": 1,
        "int": 2
    }
    for hero in heroes:
        idx = indexes.get(hero["primary_attr"])
        d["configs"][0]["categories"][idx]["hero_ids"].append(hero["id"])
    return d


def get_default_cfg_path() -> Path:
    d = f"Steam/userdata/{Config.USER_ID}/570/remote/cfg" # choose random directory in userdata if no configured user?
    
    if sys.platform == "win32":
        p = Path(f"C:/Program Files (x86)") / d
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support" / d
    elif sys.platform == "linux":
        p = Path.home() / d
    else:
        raise NotImplementedError("Hero grid directory auto detection is not supported for your OS!")
    
    return p


def update_hero_grid(data: dict, path: Path) -> None:
    """Updates hero grid config file in Steam userdata directory."""
    with open(path/"hero_grid_config.json", "w") as f:
        json_data = json.dumps(data)
        f.write(json_data)


@click.command()
@click.option("--bracket", "-b", default=DEFAULT_BRACKET)
@click.option("--path", "-p", default=None)
def main(bracket: str, path: str) -> None:
    if not any(str(e.value) == bracket for e in Brackets):
        bracket = DEFAULT_BRACKET
    
    if not path:
        cfg_path = get_default_cfg_path()
    else:
        cfg_path = Path(path)
    
    if not cfg_path.exists():
        raise ValueError(f"User cfg directory '{cfg_path}' does not exist!")
    
    # Get hero W/L stats from API
    data = get_hero_stats()

    # Sort heroes by winrate in a skill bracket
    heroes = sort_heroes_by_winrate(data, bracket=bracket)
    
    # Prepare hero grid config mapping
    heroes = format_hero_grid(heroes)
    
    # Write changes to disk
    update_hero_grid(heroes, cfg_path)
    
if __name__ == "__main__":   
    main()
