import sys
import json
import random
from enum import Enum
from pathlib import Path

import requests
import click

from config import Config
from resources import DOTA_GRID, CONFIG_BASE, CONFIG


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
    return r.json()


def sort_heroes_by_winrate(heroes: list, bracket: str) -> list:
    """Sorts list of heroes by winrate in a specific skill bracket."""
    heroes.sort(key=lambda h: h[f"{bracket}_win"] / h[f"{bracket}_pick"], reverse=True)
    return heroes
    

def create_hero_grid(heroes: list, config_name: str) -> dict:
    c = CONFIG.copy()
    c["config_name"] = config_name 
    indexes = {
        "str": 0,
        "agi": 1,
        "int": 2
    }
    for hero in heroes:
        idx = indexes.get(hero["primary_attr"])
        c["categories"][idx]["hero_ids"].append(hero["id"])
    return c


def get_cfg_path() -> Path:  
    if sys.platform == "win32":
        p = Path(f"C:/Program Files (x86)")
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support"
    elif sys.platform == "linux":
        p = Path.home()
    else:
        raise NotImplementedError("Hero grid directory auto detection is not supported for your OS!")  
    
    p = p / "Steam/userdata"

    # Choose random subdirectory if no User ID is specified.
    if not Config.USER_ID:
        p = random.choice([d for d in p.iterdir() if d.is_dir()])
    else:
        p = p / str(Config.USER_ID)

    return p / "570/remote/cfg"


def update_hero_grid(data: dict, config_name: str, path: Path) -> None:
    """Updates hero grid config file in Steam userdata directory."""
    p = path/"hero_grid_config.json"
    
    # Append to existing config if a config exists
    if p.exists():
        configs = json.load(p.open())
        for idx, config in enumerate(configs["configs"]):
            # Update existing hero grid if one exists
            if config["config_name"] == config_name:
                configs["configs"][idx] = data
                break
        else:
            configs["configs"].append(data)
        c = configs
    else:
        c = CONFIG_BASE.copy()
        c["configs"].append(data)
    
    with open(path/"hero_grid_config.json", "w") as f:
        json_data = json.dumps(c, indent="\t")
        f.write(json_data)


@click.command()
@click.option("--bracket", "-b", default=str(DEFAULT_BRACKET), type=str)
@click.option("--path", "-p", default=None)
def main(bracket: str, path: str) -> None:
    # Convert bracket name to its int representation. E.g. Herald -> 1, Guardian -> 2, etc.
    if not bracket.isdigit():
        for b in Brackets:
            if b.name.lower() == bracket.lower():
                bracket = b.value
                break

    try:
        bracket = Brackets(int(bracket))
    except ValueError:
        raise ValueError(f"Bracket '{bracket}' could not be identified.")   
    else:
        bracket = bracket.value

    # Find Steam userdata directory
    if not path:
        cfg_path = get_cfg_path()
    else:
        cfg_path = Path(path)
    if not cfg_path.exists():
        raise ValueError(f"User cfg directory '{cfg_path}' does not exist!")
    
    config_name = f"{Config.CONFIG_NAME} ({Brackets(bracket).name.capitalize()})" 

    # Get hero W/L stats from API
    data = get_hero_stats()

    # Sort heroes by winrate in a skill bracket
    heroes = sort_heroes_by_winrate(data, bracket)
    
    # Prepare hero grid config mapping
    heroes = create_hero_grid(heroes, config_name)
    
    # Write changes to disk
    update_hero_grid(heroes, config_name, cfg_path)
    
if __name__ == "__main__":   
    main()
