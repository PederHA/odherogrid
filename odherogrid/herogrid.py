import copy
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import click

from .enums import Brackets, Grouping
from .resources import (CONFIG_BASE, HERO_GRID_BASE, _get_new_category,
                        get_new_hero_grid_base)


class HeroGrid:
    def __init__(self, 
                 heroes: List[dict],
                 bracket: int,
                 config: dict,
                 grid: dict = None
                ):
        self.bracket = bracket
        self.grouping = config["grouping"]
        self.sort = config["sort"]
        self.config_name = config["config_name"]
        self.heroes = self.sort_heroes_by_winrate(heroes)

    def _fix_grid(self, config: dict) -> dict:
        """Method called by `__init__()` to verify and fix missing keys and values
        in the hero grid."""
        for key, value in HERO_GRID_BASE.items():
            if not config.get(key):
                config[key] = value # fix missing / NoneType value
        return config

    def sort_heroes_by_winrate(self, heroes: List[dict]) -> list:
        """Sorts HeroGrid instance's hero list by winrate in a specific skill bracket."""
        for hero in heroes:
            if hero["8_pick"] == 0:
                hero["8_pick"] = 1
        heroes.sort(
            key=lambda h: h[f"{self.bracket}_win"] / h[f"{self.bracket}_pick"], 
            reverse=self.sort
        )
        return heroes

    def create(self) -> dict:
        """Creates a new hero grid."""
        grouping_methods = {
            Grouping.MAINSTAT.value: self._get_grid_main_stat,
            Grouping.NONE.value: self._get_grid_all,
            Grouping.ATTACK.value: self._get_grid_attack,
            Grouping.ROLE.value: self._get_grid_role
        }
      
        meth = grouping_methods.get(self.grouping)
        if not meth:
            raise ValueError(f"No such grouping: '{self.grouping}'")
        
        hero_grid = meth()
        hero_grid["config_name"] = (f"{self.config_name} "
                                    f"({Brackets(self.bracket).name.capitalize()})")
        
        return hero_grid
        
    def modify(self, grid: dict) -> dict:
        """Modifies an existing custom hero grid."""
        # NOTE: this is terribly inefficient
        for category in grid["categories"]:
            heroes_cat = []
            for hero_id in category["hero_ids"]:
                for idx, hero in enumerate(self.heroes):
                    if hero_id == hero["id"]:
                        heroes_cat.append((hero["id"], idx)) # tuple of hero_id & index
                        break
            heroes_cat.sort(key=lambda l: l[1]) # sort by index (which corresponds to winrate)
            category["hero_ids"] = [h[0] for h in heroes_cat]
        
        return grid

    def _get_grid_main_stat(self) -> dict:
        """Creates hero grid, categorized by main stat."""
        CATEGORY_IDX = {"str": 0, "agi": 1, "int": 2} # FIXME: hardcoded values
        hero_grid = get_new_hero_grid_base()
        for hero in self.heroes: # adds heroes to categories, sorted by winrate
            idx = CATEGORY_IDX.get(hero["primary_attr"])
            hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
        return hero_grid

    def _get_grid_all(self) -> dict:
        """Creates hero grid, all heroes together in a single category."""
        category = _get_new_category("Heroes", height=1180.0)

        hero_grid = get_new_hero_grid_base()
        hero_grid["categories"] = [category] # Override predefined categories

        for hero in self.heroes:
            hero_grid["categories"][0]["hero_ids"].append(hero["id"])
        return hero_grid

    def _get_grid_attack(self) -> dict:
        """Creates hero grid, categorized by main melee/ranged."""
        melee = _get_new_category("Melee", height=280.0)
        ranged = _get_new_category("Ranged", y_pos=300.0, height=280.0)

        hero_grid = get_new_hero_grid_base()
        hero_grid["categories"] = [melee, ranged] # Override predefined categories

        for hero in self.heroes:
            idx = 1 if hero["attack_type"] == "Ranged" else 0
            hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
        return hero_grid

    def _get_grid_role(self) -> dict:
        """Creates hero grid, categorized by carry/support/flex."""
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
        self.grouping = config["grouping"]
        self.path = config["path"]
        self.sort = config["sort"]
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
                hero_grid_config = copy.deepcopy(CONFIG_BASE)
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
        # hero_grid_config.json should automatically be created by Dota 2 if it does not exist.
        # If ODHG can't find the file, the path argument is likely incorrect, hence raising 
        # this exception.
        raise FileNotFoundError(
            f"'{cfg_path}' does not exist! "
            "Verify that the correct file path has been specified."
        )

    return cfg_path


def autodetect_steam_userdata_path() -> Path:  
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
