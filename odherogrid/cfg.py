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
        raise FileNotFoundError(f"'{cfg_path}' does not exist!")

    return cfg_path


def make_new_herogrid(data: list, options: dict, bracket: int) -> None:
    config_name = f"{options['config_name']} ({Brackets(bracket).name.capitalize()})"
    grouping = options["grouping"]
    sorting = options["sort"]
    path = options["path"]

    # Create a new hero grid 
    grid = create_hero_grid(data, bracket, grouping, sorting)
    grid["config_name"] = config_name
    
    update_config(grid, config_name, path)


def modify_existing_herogrid(heroes: list, options: dict, grid_name: str, bracket: int) -> dict:
    config = load_herogrid_config(options["path"])
    
    for idx, grid in enumerate(config["configs"]):
        if grid["config_name"] == grid_name:
            grid = group_existing(grid, heroes, bracket, options["sort"])
            config["configs"][idx] = grid
            break
    else:
        names = "\n\t".join(sorted([c["config_name"] for c in config["configs"]]))
        if names:
            click.echo(
                f"Unable to locate a hero grid with the name '{grid_name}'!\n"
                f"The following hero grids were detected:\n\t{names}"
            )
        else:
            click.echo(
                "No custom hero grids could be found! "
                "The --name option should only be used sort existing hero grids."
            )
        raise SystemExit
    
    save_herogrid_config(options["path"], config)


def update_config(grid: dict, config_name: str, path: Path) -> None:
    """Updates hero grid config file in Steam userdata directory."""
    config = load_herogrid_config(path)

    # Update existing hero grid if one exists
    for idx, c in enumerate(config["configs"]):
        if c["config_name"] == config_name:
            config["configs"][idx] = grid
            break
    else:
        config["configs"].append(grid)

    save_herogrid_config(path, config)


def load_herogrid_config(path: Path) -> dict:
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


def save_herogrid_config(path: Path, config: dict) -> None:
    with open(path, "w") as f:
        json_data = json.dumps(config, indent="\t")
        f.write(json_data)
