import copy
import json
import random
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

import click
import requests

from categorize import create_hero_grid
from cfg import get_cfg_path, update_config
from config import Config
from enums import Brackets, Grouping
from parse import parse_arg_bracket, parse_arg_grouping
from resources import CATEGORY, CONFIG, CONFIG_BASE


def fetch_hero_stats() -> list:
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


@click.command()
@click.option("--bracket", "-b", default=None)
@click.option("--grouping", "-g", default=None)
@click.option("--path", "-p", default=None)
@click.option("--sort", "-s", type=click.Choice(["asc", "desc"]), default="desc")
def main(bracket: str, grouping: int, path: str, sort: str) -> None:
    # Parse arguments
    brackets = parse_arg_bracket(bracket)   # Which bracket(s) to get stats for
    grouping = parse_arg_grouping(grouping) # How heroes are categorized in the grid
    cfg_path = get_cfg_path(path)           # Get Steam userdata directory path
    sort_desc = sort == "desc"              # Ascending/descending sorting

    # Fetch hero W/L stats from API
    data = fetch_hero_stats()
    
    # Create grid for each specified bracket
    for bracket in brackets:
        config_name = f"{Config.CONFIG_NAME} ({Brackets(bracket).name.capitalize()})"
        
        # Sort heroes by winrate in the specified skill bracket
        heroes = sort_heroes_by_winrate(data, bracket, sort_desc)
        
        # Generate hero grid
        grid = create_hero_grid(heroes, grouping)
        grid["config_name"] = config_name
        
        # Save generated hero grid
        update_config(grid, config_name, cfg_path)
    
if __name__ == "__main__":   
    main()
