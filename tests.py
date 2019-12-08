import pytest

from categorize import (group_by_all, group_by_main_stat,
                        group_by_melee_ranged, group_by_role, 
                        sort_heroes_by_winrate)
from cfg import _get_steam_userdata_path, get_cfg_path
from enums import Brackets, Grouping
from odapi import fetch_hero_stats
from parseargs import parse_arg_brackets, parse_arg_grouping

PATH = r"C:\Program Files (x86)\Steam\userdata\19123403\570\remote\cfg"
stats = None
N_HEROES = 119


def _get_stats(sort: bool=False):
    global stats
    if stats is None:
        stats = fetch_hero_stats()
    if sort:
        return sort_heroes_by_winrate(stats, bracket=Brackets.DEFAULT.value)
    return stats


def _get_hero_wl(hero: dict, bracket: Brackets) -> float:
    return hero[f"{bracket.value}_win"] / hero[f"{bracket.value}_pick"]



# odapi.py
def test_opendota_api_type():
    """Tests type of data returned by `odhg.fetch_hero_stats()`"""
    heroes = _get_stats()
    assert isinstance(heroes, list)


def test_opendota_api_contents():
    """Tests type of each element in list returned by `odhg.fetch_hero_stats()`"""
    heroes = _get_stats()
    assert all(isinstance(hero, dict) for hero in heroes)


# parseargs.py
def test_parse_arg_brackets():
    """Tests every Bracket value against `odhg.parse_brackets()`"""
    brackets = [b for b in Brackets if b != Brackets.ALL]
    for b in brackets:
        assert parse_arg_brackets([str(b.value)]) == [b.value]
    assert parse_arg_brackets([1, 6, "d", "pro"]) == list(set([1, 6, 7, 8]))
    assert parse_arg_brackets([0]) == list(set([1, 2, 3, 4, 5, 6, 7, 8]))
    assert parse_arg_brackets([0, 1, 2, 3, 7]) == list(set([1, 2, 3, 4, 5, 6, 7, 8]))
    assert parse_arg_brackets([7, "d", "divine"]) == [7]


def test_parse_arg_grouping():
    """Tests every Grouping value against `odhg.parse_brackets()`"""
    for g in Grouping:
        assert parse_arg_grouping(str(g.value)) == g.value
        assert parse_arg_grouping(g.name.lower()) == g.value


# cfg.py
def test_get_cfg_path_nopath():
    """Tests `odhg.get_cfg_path()` with no argument."""
    assert _get_steam_userdata_path().exists()


def test_get_cfg_path_withpath():
    """Tests `odhg.get_cfg_path()` with valid argument."""
    assert get_cfg_path(PATH).exists()


def test_get_cfg_path_invalid_path():
    """Tests `odhg.get_cfg_path()` with invalid argument."""
    with pytest.raises(ValueError):
        assert get_cfg_path("notapath")


# enums.py
def test_brackets():
    pass


# categorize.py
def test_sort_heroes_by_winrate():
    """Tests `odhg.sort_heroes_by_winrate()`"""
    heroes = _get_stats()
    for bracket in [b for b in Brackets if b != Brackets.ALL]:
        heroes = sort_heroes_by_winrate(heroes, bracket=bracket.value)   
        for idx, hero in enumerate(heroes):
            try:
                next_hero = heroes[idx+1]
            except IndexError:
                break          
            assert _get_hero_wl(hero, bracket) >= _get_hero_wl(next_hero, bracket)


def test_group_by_main_stat():
    """Tests `categorize.group_by_main_stat()`"""
    categories = {
        "Strength": "str",
        "Agility": "agi",
        "Intelligence": "int"
    }
    stats = _get_stats(sort=True)
    conf = group_by_main_stat(stats)
    
    # Test number of categories
    assert len(conf["categories"]) == 3
    
    # Test that heroes are in appropriate categories
    for category in conf["categories"]:
        for hid in category["hero_ids"]:
            for hero in stats:
                if hero["id"] == hid:
                    assert hero["primary_attr"] == categories.get(category["category_name"])


def test_group_by_melee_ranged():
    """Tests `categorize.group_by_melee_ranged()`"""
    stats = _get_stats(sort=True)
    conf = group_by_melee_ranged(stats)
    
    # Test number of categories
    assert len(conf["categories"]) == 2
    
    # Test that heroes are in appropriate categories
    for category in conf["categories"]:
        for hid in category["hero_ids"]:
            for hero in stats:
                if hero["id"] == hid:
                    assert hero["attack_type"] == category["category_name"]


def test_group_by_role():
    """Tests `categorize.group_by_role()`"""
    stats = _get_stats(sort=True)
    conf = group_by_role(stats)
    
    # Test number of categories
    assert len(conf["categories"]) == 3
    
    # Test that heroes are in appropriate categories
    for category in conf["categories"]:
        for hid in category["hero_ids"]:
            for hero in stats:
                if hero["id"] == hid:
                    if category["category_name"] == "Flexible":
                        assert "Carry" not in hero["roles"] and "Support" not in hero["roles"]
                    else:
                        assert category["category_name"] in hero["roles"]


def test_group_by_all():
    """Tests `categorize.group_by_all()`"""
    stats = _get_stats(sort=True)
    conf = group_by_all(stats)

    # Test that there is only 1 category
    assert len(conf["categories"]) == 1

    # Test that all heroes are in the same category
    assert len(conf["categories"][0]["hero_ids"]) == N_HEROES
