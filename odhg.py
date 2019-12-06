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
from parseargs import parse_arg_brackets, parse_arg_grouping


def get_config_from_cli_arguments(**kwargs) -> dict:
    """Loads config from 'config.yml' and overrides with CLI arguments.
    
    Returns config
    """
    # Load config.yml if not all CLI arguments are passed in
    if all((v) for v in kwargs.values()):
        config = {}
    else:
        config = load_config()
    
    # Fill config with CLI arguments
    for option, value in kwargs.items():
        if value is not None:
            config[option] = value
    
    # Parse config values
    config = parse_config(config)
    
    return config


def parse_config(config: dict) -> dict:
    #config["brackets"] = parse_arg_bracket(config["bracket"])
    config["grouping"] = parse_arg_grouping(config["grouping"])
    try:
        config["path"] = get_cfg_path(config["path"])# Steam userdata directory
    except (TypeError, ValueError) as e:
        click.echo(e.args[0])
        click.echo(
            "Either specify a path using the '--path' option "
            "or run setup using the '--setup' flag")
        raise SystemExit
    return config


def make_herogrid(data: dict, config: dict, bracket: int) -> None:
    config_name = f"{config['config_name']} ({Brackets(bracket).name.capitalize()})"
    grouping = config["grouping"]
    sorting = config["sort"]
    path = config["path"]

    # Sort heroes by winrate in the specified bracket
    heroes = sort_heroes_by_winrate(data, bracket, sorting)   

    # Create a new hero grid 
    grid = create_hero_grid(heroes, grouping)
    grid["config_name"] = config_name
    
    update_config(grid, config_name, path)


@click.command()
@click.option("--brackets", "-b", default=None, type=int, multiple=True)
@click.option("--grouping", "-g", default=None)
@click.option("--path", "-p", default=None)
@click.option("--sort", "-s", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--setup", "-S", is_flag=True)
def main(brackets: str, grouping: int, path: str, sort: str, setup: bool) -> None:
    if setup:
        run_first_time_setup()
    
    config = get_config_from_cli_arguments(
        brackets=brackets, grouping=grouping, path=path
        )

    # Fetch hero W/L stats from API
    data = fetch_hero_stats()
    
    # Create grid for each specified bracket
    for bracket in config["brackets"]:
        make_herogrid(data, config, bracket)
    

# TODO: Config class?

if __name__ == "__main__":   
    main()
