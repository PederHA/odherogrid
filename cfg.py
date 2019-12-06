import copy
import json
import random
import sys
from pathlib import Path
from typing import Optional

from enums import Brackets
from resources import CONFIG_BASE
from categorize import create_hero_grid


def _get_steam_userdata_path() -> Path:  
    if sys.platform == "win32":
        p = Path("C:/Program Files (x86)")
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support"
    elif sys.platform == "linux":
        p = Path.home()
    else:
        raise NotImplementedError("Hero grid directory auto detection is not supported for your OS!")  
    
    return p / "Steam/userdata"


def get_cfg_path(path: str) -> Path:
    try:
        cfg_path = Path(path)
    except TypeError:
        raise TypeError("User cfg directory cannot be a None value!")
    if not cfg_path.exists():
        raise ValueError(f"User cfg directory '{cfg_path}' does not exist!")
    return cfg_path


def make_herogrid(data: dict, config: dict, bracket: int) -> None:
    config_name = f"{config['config_name']} ({Brackets(bracket).name.capitalize()})"
    grouping = config["grouping"]
    sorting = config["sort"]
    path = config["path"]

    # Create a new hero grid 
    grid = create_hero_grid(data, bracket, grouping, sorting)
    grid["config_name"] = config_name
    
    update_config(grid, config_name, path)


def update_config(grid: dict, config_name: str, path: Path) -> None:
    """Updates hero grid config file in Steam userdata directory."""
    p = path/"hero_grid_config.json"
    
    if p.exists():
        config = load_herogrid_config(p) # Load contents of config file if it exists
    else:
        config = copy.deepcopy(CONFIG_BASE) # Otherwise make a new config
    
    # Update existing hero grid if one exists
    for idx, c in enumerate(config["configs"]):
        if c["config_name"] == config_name:
            config["configs"][idx] = grid
            break
    else:
        config["configs"].append(grid)

    save_herogrid_config(p, config)


def load_herogrid_config(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def save_herogrid_config(path: Path, config: dict) -> None:
    with open(path, "w") as f:
        json_data = json.dumps(config, indent="\t")
        f.write(json_data)
