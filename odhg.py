import sys
import json
import random
from enum import Enum
from pathlib import Path

import requests
import click

from config import Config
from resources import DOTA_GRID, CONFIG_BASE, CONFIG


CATEGORY_IDX = {
    "str": 0,
    "agi": 1,
    "int": 2
}

class Brackets(Enum):
    HERALD = 1
    GUARDIAN = 2
    CRUSADER = 3
    ARCHON = 4
    LEGEND = 5
    ANCIENT = 6
    DIVINE = 7
    PRO = 8


DEFAULT_BRACKET = Brackets.DIVINE.value


def get_hero_stats() -> list:
    """Retrieves hero win/loss statistics from OpenDotaAPI."""
    r = requests.get("https://api.opendota.com/api/heroStats")
    heroes = r.json()
    # Rename pro_<stat> to 8_<stat>, so it's easier to work with our enum
    for hero in heroes:
        for stat in ["win", "pick", "ban"]:
            hero[f"{Brackets.PRO.value}_{stat}"] = hero.pop(f"pro_{stat}")
    return heroes


def sort_heroes_by_winrate(heroes: list, bracket: str) -> list:
    """Sorts list of heroes by winrate in a specific skill bracket."""
    heroes.sort(key=lambda h: h[f"{bracket}_win"] / h[f"{bracket}_pick"], reverse=True)
    return heroes
    

def create_hero_grid(heroes: list) -> dict:
    c = CONFIG.copy()
    for hero in heroes:
        idx = CATEGORY_IDX.get(hero["primary_attr"])
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
@click.option("--bracket", "-b")
@click.option("--path", "-p", default=None)
def main(bracket: str, path: str) -> None:
    bracket = [int(c) for c in bracket if c.isdigit()]
    
    if not bracket:
        bracket = [DEFAULT_BRACKET]
    
    brackets = []
    for b in bracket:
        try:
            b = Brackets(b)
        except ValueError:
            raise ValueError(f"Bracket '{b}' could not be identified.")   
        else:
            brackets.append(b.value)

    # Find Steam userdata directory
    if not path:
        cfg_path = get_cfg_path()
    else:
        cfg_path = Path(path)
    if not cfg_path.exists():
        raise ValueError(f"User cfg directory '{cfg_path}' does not exist!")

    # Get hero W/L stats from API
    data = get_hero_stats()
    
    for bracket in brackets:
        config_name = f"{Config.CONFIG_NAME} ({Brackets(b).name.capitalize()})"
        
        # Sort heroes by winrate in the specified skill bracket
        heroes = sort_heroes_by_winrate(data, bracket)
        
        # Generate hero grid
        grid = create_hero_grid(heroes)
        grid["config_name"] = config_name
        
        # Save generated hero grid
        update_hero_grid(grid, config_name, cfg_path)
    
if __name__ == "__main__":   
    main()
