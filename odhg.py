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
from config import load_config, run_first_time_setup
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


def get_config(**kwargs) -> None:
    """fix name"""
    config = load_config()
    for option, value in kwargs.items():
        if value is not None:
            config[option] = value
    return config


def parse_config(config: dict) -> dict:
    #config["brackets"] = parse_arg_bracket(config["bracket"])   # Which bracket(s) to get stats for
    config["grouping"] = parse_arg_grouping(config["grouping"]) # How heroes are categorized in the grid
    config["path"] = get_cfg_path(config["path"])           # Get Steam userdata directory path
    return config


@click.command()
@click.option("--brackets", "-b", default=None)
@click.option("--grouping", "-g", default=None)
@click.option("--path", "-p", default=None)
@click.option("--sort", "-s", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--setup", "-S", is_flag=True)
def main(brackets: str, grouping: int, path: str, sort: str, setup: bool) -> None:
    if setup:
        run_first_time_setup()
    
    config = get_config(brackets=brackets, grouping=grouping, path=path)
    config = parse_config(config)

    # Fetch hero W/L stats from API
    data = fetch_hero_stats()
    
    # Create grid for each specified bracket
    for bracket in config["brackets"]:
        config_name = f"{config['config_name']} ({Brackets(bracket).name.capitalize()})"
        heroes = sort_heroes_by_winrate(data, bracket, config["sort"])    
        grid = create_hero_grid(heroes, config["grouping"])
        grid["config_name"] = config["config_name"]
        
        # Save generated hero grid
        update_config(grid, config_name, config["path"])
    
if __name__ == "__main__":   
    main()
