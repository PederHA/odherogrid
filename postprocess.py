import copy

from enums import Grouping
from resources import CONFIG, CATEGORY


def create_hero_grid(heroes: list, grouping: int) -> dict:
    grouping_funcs = {
        Grouping.MAINSTAT.value: group_by_main_stat,
        Grouping.ALL.value: group_by_all,
        Grouping.ATTACK.value: group_by_melee_ranged,
        Grouping.ROLE.value: group_by_support_carry
    }
    
    grp_func = grouping_funcs.get(grouping)
    
    if not grp_func:
        raise ValueError(f"No such grouping: '{grouping}'")
    
    config = grp_func(heroes)


def group_by_main_stat(heroes: list) -> dict:
    """Get hero grid, grouped by main stat."""
    CATEGORY_IDX = {
        "str": 0,
        "agi": 1,
        "int": 2
    }
    config = _get_new_config()
    for hero in heroes:
        idx = CATEGORY_IDX.get(hero["primary_attr"])
        config["categories"][idx]["hero_ids"].append(hero["id"])
    return config


def group_by_all(heroes: list) -> dict:
    """Get hero grid, all heroes grouped together."""
    category = _get_new_category("Heroes") # TODO: Rename? xd 

    config = _get_new_config()
    config["categories"] = [category] # Override predefined categories

    for hero in heroes:
        config["categories"][0]["hero_ids"].append(hero["id"])
    return config


def group_by_melee_ranged(heroes: list) -> dict:
    """Get hero grid, grouped by main melee/ranged."""
    melee = _get_new_category("Melee")
    ranged = _get_new_category("Ranged")

    config = _get_new_config()
    config["categories"] = [melee, ranged] # Override predefined categories

    for hero in heroes:
        idx = 1 if hero["attack_type"] == "Ranged" else 0
        config["categories"][idx]["hero_ids"].append(hero["id"])
    return config


def group_by_support_carry(heroes: list) -> dict: # NOTE: Add nuker?
    """Get hero grid, grouped by support/carry."""
    support = _get_new_category("Support")
    carry = _get_new_category("Carry")

    config = _get_new_config()
    config["categories"] = [support, carry] # Override predefined categories

    for hero in heroes:
        idx = 1 if "Carry" in hero["roles"] else 0
        config["categories"][idx]["hero_ids"].append(hero["id"])
    return config


def _get_new_category(name: str) -> dict:
    category = copy.deepcopy(CATEGORY)
    category["category_name"] = name
    return category


def _get_new_config() -> dict:
    return copy.deepcopy(CONFIG)

