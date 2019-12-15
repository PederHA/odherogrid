import pytest

from pathlib import Path
from typing import List

from categorize import (group_by_all, group_by_main_stat,
                        group_by_melee_ranged, group_by_role,
                        sort_heroes_by_winrate)
from cfg import _get_steam_userdata_path, get_cfg_path
from config import (CONFIG_BASE, _check_config_integrity, _load_config,
                    _parse_user_bracket_input)
from enums import Brackets, Grouping
from odapi import fetch_hero_stats
from odhg import parse_config
from parseargs import parse_arg_brackets, parse_arg_grouping

PATH = r"C:\Program Files (x86)\Steam\userdata\19123403\570\remote\cfg"
stats = None
N_HEROES = 119


def _get_stats(sort: bool=False) -> List[dict]:
    global stats
    if stats is None:
        stats = fetch_hero_stats()
    if sort:
        return sort_heroes_by_winrate(stats, bracket=Brackets.DEFAULT.value)
    return stats


def _get_hero_wl(hero: dict, bracket: Brackets) -> float:
    return hero[f"{bracket.value}_win"] / hero[f"{bracket.value}_pick"]


@pytest.fixture
def heroes():
    return _get_hero_stats()


@pytest.fixture
def heroes_sorted():
    return _get_hero_stats(sort=True)


# odhg.py
def test_parse_config():
    """
    `odhg.parse_config()`

    Not a very good test.
    """
    config = _load_config()
    config = parse_config(config)
    for v in config.values():
        assert v is not None


# odapi.py
def test_opendota_api():
    """Tests type of data returned by `odhg.fetch_hero_stats()`"""
    heroes = _get_stats()
    
    # Ensure data returned by fetch_hero_stats() is a list
    assert isinstance(heroes, list)

    # Ensure all heroes are included
    assert len(heroes) == N_HEROES
    
    # Verify that all elements in heroes list are dicts
    assert all(isinstance(hero, dict) for hero in heroes)


# parseargs.py
def test_parse_arg_brackets():
    """Tests every Bracket value against `odhg.parse_brackets()`"""
    for b in [b for b in Brackets if b != Brackets.ALL]:
        assert parse_arg_brackets([str(b.value)]) == [b.value]
        assert parse_arg_brackets([b.value]) == [b.value]
    
    # Mix of ints, chars and strings
    assert parse_arg_brackets([1, 6, "d", "pro"]) == list(set([1, 6, 7, 8]))
    
    # 0 as arg
    assert parse_arg_brackets([0]) == list(set([1, 2, 3, 4, 5, 6, 7, 8]))
    assert parse_arg_brackets(["0"]) == list(set([1, 2, 3, 4, 5, 6, 7, 8]))
    assert parse_arg_brackets([0, 1, 2, 3, 7]) == list(set([1, 2, 3, 4, 5, 6, 7, 8]))
    
    # Identical arguments of different values
    assert parse_arg_brackets([7, "d", "divine"]) == [7]

    # Duplicate arguments
    assert parse_arg_brackets([7, 7, 7]) == [7]


def test_parse_arg_grouping():
    """Tests every Grouping value against `odhg.parse_brackets()`"""
    for g in Grouping:
        assert parse_arg_grouping(str(g.value)) == g.value
        assert parse_arg_grouping(g.name.lower()) == g.value


# cfg.py
def test_get_cfg_path_nopath():
    """Tests `odhg.get_cfg_path()` with no argument."""
    assert _get_steam_userdata_path().exists()


def test_get_cfg_path():
    # Test with existing path
    assert get_cfg_path(PATH).exists()
    
    # Test with nonexistant path
    with pytest.raises(ValueError):
        assert get_cfg_path("notapath")


# enums.py
def test_brackets_default():
    assert Brackets(Brackets.DEFAULT)


def test_grouping_default():
    assert Grouping(Grouping.DEFAULT)


# categorize.py
def test_sort_heroes_by_winrate():
    """Tests `categorize.sort_heroes_by_winrate()`"""
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


# config.py
def test__load_config():
    """Tests `config._load_config()`"""
    p = Path("config.yml")
    if p.exists():
            if p.stat().st_size > 0:
                assert _load_config()
            else:
                with pytest.raises(ValueError):
                    assert _load_config()
    else:
        with pytest.raises(FileNotFoundError):
            assert _load_config()


def test__check_config_integrity():
    assert _check_config_integrity(CONFIG_BASE) == CONFIG_BASE


def test__parse_user_bracket_input():
    assert _parse_user_bracket_input("1 2 7") == [1, 2, 7]
    assert _parse_user_bracket_input("1 q 7") == [1, 7]
    assert _parse_user_bracket_input("1 2 divine") == [1, 2]
    assert _parse_user_bracket_input("1 2 3 4 5 6 7 8") == [1, 2, 3, 4, 5, 6, 7, 8]
    assert _parse_user_bracket_input("7 7 7") == [7]
