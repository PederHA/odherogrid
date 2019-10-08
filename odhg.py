import copy
import json
import random
import sys
from enum import Enum
from pathlib import Path
from typing import Optional, List

import click
import requests

from cfg import get_cfg_path, update_config
from config import Config
from postprocess import create_hero_grid
from resources import CONFIG, CONFIG_BASE, CATEGORY


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


class Grouping(Enum):
    ALL = 0
    MAINSTAT = 1
    ATTACK = 2
    ROLE = 3
    

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


def get_brackets(bracket: Optional[str]) -> List[int]:
    # Parse bracket argument(s)
    if not bracket:
        brackets = [DEFAULT_BRACKET] # '' -> [7]
    elif bracket == str(Brackets.ALL.value):
        brackets = [b.value for b in Brackets if b.value != b.ALL.value] # '9' -> [1, 2, 3, .., 8]
    else:
        brackets = [int(c) for c in bracket if c.isdigit()] # '178' -> [1, 7, 8]

    for b in brackets:
        try:
            Brackets(b)
        except ValueError:
            raise ValueError(f"Bracket '{b}' could not be identified.")

    return brackets


@click.command()
@click.option("--bracket", "-b")
@click.option("--path", "-p", default=None)
@click.option("--sort", "-s", type=click.Choice(["asc", "desc"]), default="desc")
def main(bracket: str, path: str, sort: str) -> None:
    # Parse arguments
    brackets = get_brackets(bracket)
    cfg_path = get_cfg_path(path) # Find Steam userdata directory
    sort_desc = sort == "desc" # Ascending/descending

    # Get hero W/L stats from API
    data = get_hero_stats()
    
    # Create grid for each specified bracket
    for bracket in brackets:
        config_name = f"{Config.CONFIG_NAME} ({Brackets(bracket).name.capitalize()})"
        
        # Sort heroes by winrate in the specified skill bracket
        heroes = sort_heroes_by_winrate(data, bracket, sort_desc)
        
        # Generate hero grid
        grid = create_hero_grid(heroes)
        grid["config_name"] = config_name
        
        # Save generated hero grid
        update_config(grid, config_name, cfg_path)
    
if __name__ == "__main__":   
    main()
