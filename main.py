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
    r = requests.get("https://api.opendota.com/api/heroStats")
    heroes = r.json()
    return heroes


def sort_heroes_by_winrate(heroes: list, bracket: str) -> list:
    heroes.sort(key=lambda h: h[f"{bracket}_pick"] / h[f"{bracket}_win"])
    return heroes

def categorize_heroes_by_stat(heroes: list) -> dict:
    heroes = {}
    

def format_hero_grid(heroes: List[int]) -> dict:
    d = DOTA_GRID.copy()
    d["configs"][0]["categories"][0]["hero_ids"].extend(heroes)
    return d


def get_default_cfg_path() -> Path:
    d = f"Steam/userdata/{Config.USER_ID}/570/remote/cfg" # choose random directory in userdata if no configured user?
    
    if sys.platform == "win32":
        p = Path(f"C:/Program Files(x86)") / d
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support" / d
    elif sys.platform == "linux":
        p = Path.home() / d
    else:
        raise NotImplementedError("Hero grid directory auto detection is not supported for your OS!")
    
    return p


def update_hero_grid(path: Path, data: dict) -> None:
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
    
    heroes = sort_heroes_by_winrate(get_hero_stats(), bracket=bracket)

    update_hero_grid(cfg_path, data)
    
if __name__ == "__main__":   
    main()
