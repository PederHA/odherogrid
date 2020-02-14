import itertools

import pytest

from odherogrid.enums import Bracket, Layout
from odherogrid.herogrid import (HeroGrid, HeroGridConfig,
                                 detect_userdata_path,
                                 get_hero_grid_config_path)


def _get_hero_wl(hero: dict, bracket: Bracket) -> float:
    return hero[f"{bracket.value}_win"] / hero[f"{bracket.value}_pick"]


def test_herogridconfig_create_grids(heroes, testconf_dict):
    """Tests `HeroGridConfig.create_grids()` with all combinations
     of brackets and layout."""
    conf = testconf_dict
    brackets = [b for b in Bracket if b != 0] # don't include ALL
    for bracket, layout in itertools.product(brackets, Layout):
        conf["brackets"] = [bracket]
        conf["layout"] = layout
        name = f"{bracket}{layout}"
        conf["config_name"] = name
        h = HeroGridConfig(heroes, conf)
        h.create_grids()
        assert next(
            c for c in h.hero_grid_config["configs"] 
            if c["config_name"] == f"{name} ({Bracket(bracket).name.capitalize()})"
        )


def test_herogridconfig_add_grid(herogridconfig: HeroGridConfig):
    grid = {"config_name": "testgrid", 
            "categories": [
            ]
        }
    herogridconfig.add_hero_grid(grid)

    # Assert that config has been added
    assert next( # next just yields the first grid with matching name
        g for g in herogridconfig.hero_grid_config["configs"] 
        if grid["config_name"] == g["config_name"]
    )


def test_herogridconfig_save_grid(herogridconfig: HeroGridConfig):
    herogridconfig.save_hero_grid_config()
    herogridconfig.save_hero_grid_config(path=herogridconfig.config["path"])


def _check_herogrid(name: str, grid: dict):
    # x in herogrid bla bla bla
    pass


def test_sort_heroes_by_winrate(heroes, testconf_dict):
    """Tests `HeroGrid.sort_heroes_by_winrate()`"""
    config = testconf_dict
    for bracket in [b for b in Bracket if b != Bracket.ALL]:
        h = HeroGrid(heroes, bracket, config)
        h.sort_heroes_by_winrate()
        for idx, hero in enumerate(h.heroes):
            try:
                next_hero = h.heroes[idx+1]
            except IndexError:
                break          
            assert _get_hero_wl(hero, bracket) >= _get_hero_wl(next_hero, bracket)


def test_get_cfg_path_nopath():
    """Tests userdata directory auto-detection."""
    assert detect_userdata_path().exists()



def test_get_cfg_path():
    """Test with default config path"""
    with pytest.raises(FileNotFoundError):
        assert get_hero_grid_config_path("SOMEPATH")


def test_get_cfg_path_invalid():
    """Test with nonexistant path"""
    with pytest.raises(FileNotFoundError):
        assert get_hero_grid_config_path("notapath")


def test_get_cfg_path_none():
    """Test with nonexistant path"""
    with pytest.raises(TypeError) as e:
        assert get_hero_grid_config_path(None)
    assert e.exconly() == "TypeError: hero grid config path cannot be a None value!"



def test_herogrid__get_grid_main_stat(heroes, herogrid: HeroGrid):
    """Tests `HeroGrid._get_grid_main_stat()`"""
    categories = {
        "Strength": "str",
        "Agility": "agi",
        "Intelligence": "int"
    }
    grid = herogrid._get_grid_main_stat()
    
    # Test number of categories
    assert len(grid["categories"]) == 3
    
    # Test that heroes are in appropriate categories
    for category in grid["categories"]:
        for hid in category["hero_ids"]:
            for hero in heroes:
                if hero["id"] == hid:
                    assert hero["primary_attr"] == categories.get(category["category_name"])


def test_herogrid__get_grid_attack(heroes, herogrid: HeroGrid):
    """Tests `HeroGrid._get_grid_attack()`"""
    grid = herogrid._get_grid_attack()
    
    # Test number of categories
    assert len(grid["categories"]) == 2
    
    # Test that heroes are in appropriate categories
    for category in grid["categories"]:
        for hid in category["hero_ids"]:
            for hero in heroes:
                if hero["id"] == hid:
                    assert hero["attack_type"] == category["category_name"]


def test_herogrid__get_grid_role(heroes, herogrid: HeroGrid):
    """Tests `HeroGrid._get_grid_role()`"""
    grid = herogrid._get_grid_role()
    
    # Test number of categories
    assert len(grid["categories"]) == 3
    
    # Test that heroes are in appropriate categories
    for category in grid["categories"]:
        for hid in category["hero_ids"]:
            for hero in heroes:
                if hero["id"] == hid:
                    if category["category_name"] == "Flexible":
                        assert "Carry" not in hero["roles"] and "Support" not in hero["roles"]
                    else:
                        assert category["category_name"] in hero["roles"]


def test_herogrid__get_grid_single(heroes, N_HEROES, herogrid: HeroGrid):
    """Tests `HeroGrid._get_grid_single()`"""
    grid = herogrid._get_grid_single()
    
    # Test that there is only 1 category
    assert len(grid["categories"]) == 1

    # Test that all heroes are in the same category
    assert len(grid["categories"][0]["hero_ids"]) == N_HEROES