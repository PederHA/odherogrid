"""
Functions for loading, modifying and updating `hero_grid_config.json`,
which is the file in which Dota 2 hero grid layouts are stored.
"""

import copy
import json
import random
import sys
from pathlib import Path
from typing import Optional

import click

from .enums import Brackets
from .resources import CONFIG_BASE
from .categorize import create_hero_grid, group_existing


def _autodetect_steam_userdata_path() -> Path:  
    if sys.platform == "win32":
        p = Path("C:/Program Files (x86)")
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support"
    elif sys.platform == "linux":
        p = Path.home()
    else:
        raise NotImplementedError("Userdata directory auto-detection is not supported for your OS!")  
    
    p = p / "Steam/userdata"
    if not p.exists():
        raise FileNotFoundError("Unable to automatically detect userdata directory!")

    return p


def get_hero_grid_config_path(path: str) -> Path:
    try:
        cfg_path = Path(path)
    except TypeError as e:
        if e.args and "not NoneType" in e.args[0]: # provide a nicer exception string
            raise TypeError("hero grid config path cannot be a None value!")
        else:
            raise
    
    # Append hero grid config filename if only a directory path is provided
    if cfg_path.name != "hero_grid_config.json":
        cfg_path = cfg_path / "hero_grid_config.json"
    
    if not cfg_path.exists():
        # hero_grid_config.json should automatically be created by Dota 2 if it does not exist.
        # If ODHG can't find the file, the path argument is likely incorrect, hence raising 
        # this exception.
        raise FileNotFoundError(
            f"'{cfg_path}' does not exist! "
            "Verify that the correct file path has been specified."
        )

    return cfg_path


def make_new_herogrids(data: list, options: dict) -> None:
    """Creates a new hero grid based on the parameters passed in.
    
    Parameters
    ----------
    data : list
        Hero win/loss data from OpenDota API
    options : dict
        CLI/Config options
    """
    # Get parameters
    grouping = options["grouping"]
    sorting = options["sort"]
    path = options["path"]

    # Load existing config
    hero_grid_config = load_hero_grid_config(path)

    # Create new hero grids for the specified brackets
    for bracket in options["brackets"]:
        grid = create_hero_grid(data, bracket, grouping, sorting)
        grid["config_name"] = f"{options['config_name']} ({Brackets(bracket).name.capitalize()})"
        hero_grid_config = update_hero_grid_config(hero_grid_config, grid)
    
    save_hero_grid_config(hero_grid_config, path)


def modify_existing_herogrid(heroes: list, options: dict, grid_name: str) -> dict:
    # Load existing config
    config = load_hero_grid_config(options["path"])
    
    # Look for a hero grid with the specified grid_name
    for idx, grid in enumerate(config["configs"]):
        if grid["config_name"] == grid_name:
            grid = group_existing(grid, heroes, options["brackets"][0], options["sort"])
            config["configs"][idx] = grid
            break
    else:
        # The else-branch is only entered if no matching hero grid could be found
        names = "\n\t".join(sorted([c["config_name"] for c in config["configs"]]))
        if names:
            click.echo(
                f"Unable to locate a hero grid with the name '{grid_name}'!\n"
                f"The following hero grids were detected:\n\t{names}"
            )
        else:
            click.echo(
                "No custom hero grids could be found! "
                "The --name option should only be used to sort existing hero grids."
            )
        raise SystemExit
    
    save_hero_grid_config(options["path"], config)


def update_hero_grid_config(hero_grid_config: dict, hero_grid: dict) -> dict:
    """Updates hero grid configuration with a new hero grid.
    If a hero grid already exists with the same name, it is overwritten
    by the new hero grid."""
    # Update existing hero grid if one exists
    for idx, c in enumerate(hero_grid_config["configs"]):
        if c["config_name"] == hero_grid["config_name"]:
            hero_grid_config["configs"][idx] = hero_grid
            break
    else:
        hero_grid_config["configs"].append(hero_grid)
    
    return hero_grid_config


def load_hero_grid_config(path: Path) -> dict:
    """Attempts to load hero_grid_config.json. Returns empty config
    if file is empty or malformed."""
    with open(path, "r") as f:
        try:
            hero_grid_config = json.load(f)
        except json.JSONDecodeError:
            click.echo(f"{path} is empty or malformed. A new config will be created.")
            return copy.deepcopy(CONFIG_BASE)
        else:
            return hero_grid_config


def save_hero_grid_config(hero_grid_config: dict, path: Path) -> None:
    with open(path, "w") as f:
        json_data = json.dumps(hero_grid_config, indent="\t")
        f.write(json_data)
