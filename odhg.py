import sys
import json
import random
import copy
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
    PRO = 8
    ALL = 9


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


def sort_heroes_by_winrate(heroes: list, bracket: str, descending: bool=True) -> list:
    """Sorts list of heroes by winrate in a specific skill bracket."""
    heroes.sort(key=lambda h: h[f"{bracket}_win"] / h[f"{bracket}_pick"], reverse=descending)
    return heroes
    

def create_hero_grid(heroes: list) -> dict:
    CATEGORY_IDX = {
        "str": 0,
        "agi": 1,
        "int": 2
    }
    c = copy.deepcopy(CONFIG)
    for hero in heroes:
        idx = CATEGORY_IDX.get(hero["primary_attr"])
        c["categories"][idx]["hero_ids"].append(hero["id"])
    return c


def get_cfg_path() -> Path:  
    if sys.platform == "win32":
        p = Path("C:/Program Files (x86)")
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


def update_config(grid: dict, config_name: str, path: Path) -> None:
    """Updates hero grid config file in Steam userdata directory."""
    p = path/"hero_grid_config.json"
    
    # Append to existing config if a config exists
    if p.exists():
        configs = json.load(p.open())
        for idx, config in enumerate(configs["configs"]):
            # Update existing hero grid if one exists
            if config["config_name"] == config_name:
                configs["configs"][idx] = grid
                break
        else:
            configs["configs"].append(grid)
        c = configs
    else:
        c = copy.deepcopy(CONFIG_BASE)
        c["configs"].append(grid)
    
    with open(path/"hero_grid_config.json", "w") as f:
        json_data = json.dumps(c, indent="\t")
        f.write(json_data)


@click.command()
@click.option("--bracket", "-b")
@click.option("--path", "-p", default=None)
@click.option("--sort", "-s", type=click.Choice(["asc", "desc"]), default="desc")
def main(bracket: str, path: str, sort: str) -> None:
    # Parse bracket argument(s)
    if not bracket:
        bracket = [DEFAULT_BRACKET] # '' -> [7]
    elif bracket == str(Brackets.ALL.value):
        bracket = [b.value for b in Brackets if b.value != b.ALL.value] # '9' -> [1, 2, 3, .., 8]
    else:
        bracket = [int(c) for c in bracket if c.isdigit()] # '178' -> [1, 7, 8]

    for b in bracket:
        try:
            Brackets(b)
        except ValueError:
            raise ValueError(f"Bracket '{b}' could not be identified.")   
    brackets = bracket

    # Find Steam userdata directory
    if not path:
        cfg_path = get_cfg_path()
    else:
        cfg_path = Path(path)
    if not cfg_path.exists():
        raise ValueError(f"User cfg directory '{cfg_path}' does not exist!")

    descending = sort == "desc"

    # Get hero W/L stats from API
    data = get_hero_stats()
    
    for bracket in brackets:
        config_name = f"{Config.CONFIG_NAME} ({Brackets(bracket).name.capitalize()})"
        
        # Sort heroes by winrate in the specified skill bracket
        heroes = sort_heroes_by_winrate(data, bracket, descending)
        
        # Generate hero grid
        grid = create_hero_grid(heroes)
        grid["config_name"] = config_name
        
        # Save generated hero grid
        update_config(grid, config_name, cfg_path)
    
if __name__ == "__main__":   
    main()
