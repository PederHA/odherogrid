import copy
from typing import Union, List

from .enums import Grouping
from .resources import HERO_GRID_BASE, CATEGORY_BASE


def sort_heroes_by_winrate(heroes: List[dict], bracket: str, descending: bool=True) -> list:
    """Sorts list of heroes by winrate in a specific skill bracket."""
    for hero in heroes:
        if hero["8_pick"] == 0:
            hero["8_pick"] = 1
    heroes.sort(key=lambda h: h[f"{bracket}_win"] / h[f"{bracket}_pick"], reverse=descending)
    return heroes


def create_hero_grid(heroes: List[dict], bracket: int, grouping: int, sorting: bool) -> dict:
    grouping_funcs = {
        Grouping.MAINSTAT.value: group_by_main_stat,
        Grouping.NONE.value: group_by_all,
        Grouping.ATTACK.value: group_by_melee_ranged,
        Grouping.ROLE.value: group_by_role
    }
    # Sort heroes by winrate in the specified bracket
    heroes = sort_heroes_by_winrate(heroes, bracket, sorting)       
    
    grp_func = grouping_funcs.get(grouping)
    if not grp_func:
        raise ValueError(f"No such grouping: '{grouping}'")
    
    hero_grid = grp_func(heroes)
    
    return hero_grid


def group_by_main_stat(heroes: List[dict]) -> dict:
    """Creates hero grid, categorized by main stat."""
    CATEGORY_IDX = {
        "str": 0,
        "agi": 1,
        "int": 2
    }
    hero_grid = _get_new_hero_grid_base()
    for hero in heroes:
        idx = CATEGORY_IDX.get(hero["primary_attr"])
        hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
    return hero_grid


def group_by_all(heroes: List[dict]) -> dict:
    """Creates hero grid, all heroes together in a single category."""
    category = _get_new_category("Heroes", height=1180.0)

    hero_grid = _get_new_hero_grid_base()
    hero_grid["categories"] = [category] # Override predefined categories

    for hero in heroes:
        hero_grid["categories"][0]["hero_ids"].append(hero["id"])
    return hero_grid


def group_by_melee_ranged(heroes: List[dict]) -> dict:
    """Creates hero grid, categorized by main melee/ranged."""
    melee = _get_new_category("Melee", height=280.0)
    ranged = _get_new_category("Ranged", y_pos=300.0, height=280.0)

    hero_grid = _get_new_hero_grid_base()
    hero_grid["categories"] = [melee, ranged] # Override predefined categories

    for hero in heroes:
        idx = 1 if hero["attack_type"] == "Ranged" else 0
        hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
    return hero_grid


def group_by_role(heroes: List[dict]) -> dict:
    """Creates hero grid, categorized by carry/support/flex."""
    carry = _get_new_category("Carry")
    support = _get_new_category("Support", y_pos=200.0)
    flex = _get_new_category("Flexible", y_pos=400.0)

    hero_grid = _get_new_hero_grid_base()
    hero_grid["categories"] = [carry, support, flex] # Override predefined categories

    for hero in heroes:
        if "Carry" in hero["roles"]:
            idx = 0 
        elif "Support" in hero["roles"]:
            idx = 1
        else:
            idx = 2
        hero_grid["categories"][idx]["hero_ids"].append(hero["id"])
    return hero_grid


def group_existing(config: dict, heroes: List[dict], bracket: int, sort_desc: bool) -> dict:
    """Modifies an existing herogrid."""
    heroes = sort_heroes_by_winrate(heroes, bracket, sort_desc)
    
    # NOTE: this is terribly inefficient
    for category in config["categories"]:
        heroes_cat = []
        for hero_id in category["hero_ids"]:
            for idx, hero in enumerate(heroes):
                if hero_id == hero["id"]:
                    heroes_cat.append((hero["id"], idx)) # tuple of hero_id & index
                    break
        heroes_cat.sort(key=lambda l: l[1]) # sort by index (which corresponds to winrate)
        category["hero_ids"] = [h[0] for h in heroes_cat]
    
    return config


def _get_new_category(name: str, x_pos: float=0.0, y_pos: float=0.0, width: float=0.0, height: float=0.0) -> dict:
    # Copy category and give it a name
    category = copy.deepcopy(CATEGORY_BASE)
    category["category_name"] = name

    params = {
        "x_position": x_pos,
        "y_position": y_pos,
        "width": width,
        "height": height
    }
    for param, value in params.items():
        value = float(abs(value)) # ensure value is a positive float
        if value:
            category[param] = value

    return category


def _get_new_hero_grid_base() -> dict:
    return copy.deepcopy(HERO_GRID_BASE)
