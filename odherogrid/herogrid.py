import copy
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import click

from .enums import Bracket, Layout
from .resources import (HERO_GRID_CONFIG_BASE, HERO_GRID_BASE, _get_new_category,
                        get_new_hero_grid_base)


class HeroGrid:
    def __init__(self, 
                 heroes: List[dict],
                 bracket: int,
                 config: dict,
                 grid: dict = None
                ):
        self.bracket = bracket
        self.layout = config["layout"]
        self.ascending = config["ascending"]
        self.config_name = config["config_name"]
        self.heroes = heroes
        self.sort_heroes_by_winrate()
        # TODO: add _fix_grid tests before using it

    def _fix_grid(self, config: dict) -> dict:
        """Method called by `__init__()` to verify and fix missing keys and values
        in the hero grid."""
        for key, value in HERO_GRID_BASE.items():
            if not config.get(key):
                config[key] = value # fix missing / NoneType value
        return config

    def sort_heroes_by_winrate(self) -> list:
        """Sorts HeroGrid hero list by winrate in a specific skill bracket."""
        for hero in self.heroes:
            if hero["8_pick"] == 0:
                hero["8_pick"] = 1
        self.heroes.sort(
            key=lambda h: h[f"{self.bracket}_win"] / h[f"{self.bracket}_pick"], 
            reverse=not self.ascending
        )

    def create(self) -> dict:
        """Creates a new hero grid."""
        layout_methods = {
            Layout.MAINSTAT.value: self._get_grid_main_stat,
            Layout.SINGLE.value: self._get_grid_single,
            Layout.ATTACK.value: self._get_grid_attack,
            Layout.ROLE.value: self._get_grid_role
        }
      
        meth = layout_methods.get(self.layout)
        if not meth:
            raise ValueError(f"No such layout: '{self.layout}'")
        
        hero_grid = meth()
        hero_grid["config_name"] = (f"{self.config_name} "
                                    f"({Bracket(self.bracket).name.capitalize()})")
        
        return hero_grid
        
    def modify(self, grid: dict) -> dict:
        """Modifies an existing hero grid."""
        hero_idx: Dict[int, int] = {
            hero["id"]: idx for idx, hero in enumerate(self.heroes)
        }
        for category in grid["categories"]:
            heroes_cat = []
            for hero_id in category["hero_ids"]:
                idx = hero_idx.get(hero_id)
                if idx is None:
                    # TODO: handle error
                    print(f"Unable to find index for hero with ID {hero_id}")
                    continue
                heroes_cat.append((hero_id, idx)) # tuple of hero_id & index
            heroes_cat.sort(key=lambda l: l[1]) # sort by index (which corresponds to winrate)
            category["hero_ids"] = [h[0] for h in heroes_cat]
        
        return grid

    def _get_grid_main_stat(self) -> dict:
        """Creates a hero grid with a mainstat layout (Dota 2 default)."""
        CATEGORY_IDX = {"str": 0, "agi": 1, "int": 2}
        hero_grid = get_new_hero_grid_base()
        for hero in self.heroes: # adds heroes to categories, sorted by winrate
            idx = CATEGORY_IDX.get(hero["primary_attr"])
            hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
        return hero_grid

    def _get_grid_single(self) -> dict:
        """Creates a hero grid with a single category layout."""
        category = _get_new_category("Heroes", height=1180.0)

        hero_grid = get_new_hero_grid_base()
        hero_grid["categories"] = [category] # Override predefined categories

        for hero in self.heroes:
            hero_grid["categories"][0]["hero_ids"].append(hero["id"])
        return hero_grid

    def _get_grid_attack(self) -> dict:
        """Creates a hero grid with a melee/range attack type layout."""
        melee = _get_new_category("Melee", height=280.0)
        ranged = _get_new_category("Ranged", y_pos=300.0, height=280.0)

        hero_grid = get_new_hero_grid_base()
        hero_grid["categories"] = [melee, ranged] # Override predefined categories

        for hero in self.heroes:
            idx = 1 if hero["attack_type"] == "Ranged" else 0
            hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
        return hero_grid

    def _get_grid_role(self) -> dict:
        """Creates a hero grid with a hero role layout (Carry/Support/Flex)."""
        carry = _get_new_category("Carry")
        support = _get_new_category("Support", y_pos=200.0)
        flex = _get_new_category("Flexible", y_pos=400.0)

        hero_grid = get_new_hero_grid_base()
        hero_grid["categories"] = [carry, support, flex] # Override predefined categories

        for hero in self.heroes:
            if "Carry" in hero["roles"]:
                idx = 0 
            elif "Support" in hero["roles"]:
                idx = 1
            else:
                idx = 2
            hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
        return hero_grid


class HeroGridConfig:
    def __init__(self, heroes: List[dict], config: dict) -> None:
        self.heroes = heroes

        # Config keys
        self.config = config

        # NOTE: Do we need these?
        self.brackets = config["brackets"]
        self.layout = config["layout"]
        self.path = config["path"]
        self.ascending = config["ascending"]
        self.config_name = config["config_name"]

        self.hero_grid_config = self.load_hero_grid_config()
        # TODO: _fix_hero_grid_config() ?
        self.grids = [] # List of grids created by this instance. see: add_hero_grid()

    def create_grids(self) -> List[dict]:
        for bracket in self.brackets:
            h = HeroGrid(self.heroes, bracket, self.config)
            grid = h.create()
            self.add_hero_grid(grid)

        self.save_hero_grid_config()

    def modify_grid(self, name: str) -> List[dict]:
        # Attempt to find a grid with matching name
        grid = self._get_grid(name)
        
        # NOTE: Prompt to select specific skill bracket?
        h = HeroGrid(self.heroes, self.brackets[0], self.config)
        grid = h.modify(grid)

        self.add_hero_grid(grid)
        self.save_hero_grid_config()

    def _get_grid(self, name: str) -> dict:
        """Attempts to find a grid by the given name. TODO: Expand description"""
        try:
            # find first grid with matching name
            grid = next(
                g for g in self.hero_grid_config["configs"] 
                if g["config_name"] == name
            )
        except StopIteration:
            gridnames = "\n\t".join(
                sorted(
                    [c["config_name"] for c in self.hero_grid_config["configs"]]
                )
            )
            if gridnames:
                click.echo(
                    f"Unable to locate a hero grid with the name '{name}'!\n"
                    f"The following hero grids were detected:\n\t{gridnames}"
                )
            else:
                click.echo(
                    "No custom hero grids could be found! "
                    "The --name option should only be used to sort existing hero grids."
                )
            raise SystemExit 
        else:
            return grid
    
    def add_hero_grid(self, grid: dict, *, overwrite: bool=True) -> None:
        """Adds a hero grid to the hero grid config.
        NOTE:
        ----
        No methods currently make use of the `overwrite` parameter.
        """
        name = grid["config_name"]
        for idx, g in enumerate(self.hero_grid_config["configs"]):
            if g["config_name"] == name:
                if overwrite:
                    self.hero_grid_config["configs"][idx] = grid
                else:
                    raise KeyError(
                        f"A hero grid with the name '{name}' already exists!"
                    )
                break
        else:
            self.hero_grid_config["configs"].append(grid)

        self.grids.append(grid)

    def load_hero_grid_config(self, *, path: Path=None) -> dict:
        """Loads hero_grid_config.json and parses it."""
        p = path or self.path
        with open(p, "r") as f:
            try:
                hero_grid_config = json.load(f)
            except json.JSONDecodeError:
                # Renames broken config and returns an empty config
                # TODO: Verify hero_grid_config.json integrity
                click.echo(f"{p} is empty or malformed. A new config will be created.")
                name = f"hero_grid_config_INVALID_{datetime.now().isoformat()}.json"
                p.rename(p.stem / name)
                click.echo(f"The existing config was renamed to '{name}'")
                hero_grid_config = copy.deepcopy(HERO_GRID_CONFIG_BASE)
            finally:
                return hero_grid_config

    def save_hero_grid_config(self, *, path: Path=None) -> None:
        p = path or self.path
        with open(p, "w") as f:
            json_data = json.dumps(self.hero_grid_config, indent="\t")
            f.write(json_data)


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
        # Create new empty hero_grid_config.json
        _new_hero_grid_config(cfg_path)

    return cfg_path


def _new_hero_grid_config(path: Path) -> None:
    config = json.dumps(HERO_GRID_CONFIG_BASE)
    with open(path, "w", encoding="utf-8") as f:  
        f.write(config)


# NOTE: should this function reside in config.py instead?
def detect_userdata_path() -> Path:  
    if sys.platform == "win32":
        p = _get_steam_path_windows()
    elif sys.platform == "darwin":
        # NYI: Mac OS steam path detection
        p = Path.home() / "Library/Application Support/Steam"
    elif sys.platform == "linux":
        # NYI: Mac OS steam path detection
        p = Path.home() / "Steam"
    else:
        raise NotImplementedError("Userdata directory auto-detection is not supported for your OS!")  
    
    p = p / "userdata"
    if not p.exists():
        raise FileNotFoundError("Unable to automatically detect userdata directory!")

    return p

def _get_steam_path_windows(default: str="C:\\Program Files (x86)\\Steam") -> Path:
    import winreg
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", 0, winreg.KEY_READ)
    try:
        value, _ = winreg.QueryValueEx(key, "InstallPath")
    except FileNotFoundError:
        value = default
        click.echo(
            "Unable to locate steam folder automatically. "
            f"Defaulting to {value}"
        )
    return Path(value)

