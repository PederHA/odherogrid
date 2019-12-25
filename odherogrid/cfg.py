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


def get_cfg_path(path: str) -> Path:
    try:
        cfg_path = Path(path)
    except TypeError:
        raise TypeError("User cfg directory cannot be a None value!")
    if not cfg_path.exists():
        raise ValueError(f"User cfg directory '{cfg_path}' does not exist!")
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
    save_herogrid_config(options["path"], config)


def update_config(grid: dict, config_name: str, path: Path) -> None:
    """Updates hero grid config file in Steam userdata directory."""
    # Load contents of file if it exists
    if path.exists():
        config = load_herogrid_config(path) # Load contents of config file if it exists
    else:
        config = None
    
    # check config contents     
    if not config or not config.get("configs"):
        config = copy.deepcopy(CONFIG_BASE) # make new config
    
    # Update existing hero grid if one exists
    for idx, c in enumerate(config["configs"]):
        if c["config_name"] == config_name:
            config["configs"][idx] = grid
            break
    else:
        config["configs"].append(grid)

    save_herogrid_config(path, config)


def load_herogrid_config(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def save_herogrid_config(path: Path, config: dict) -> None:
    with open(path, "w") as f:
        json_data = json.dumps(config, indent="\t")
        f.write(json_data)
