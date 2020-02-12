import itertools
import random
import shutil
import sys
from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import List

import pytest


# DELETE
from odherogrid.categorize import (_get_new_category, create_hero_grid,
                                   group_by_all, group_by_main_stat,
                                   group_by_melee_ranged, group_by_role,
                                   sort_heroes_by_winrate)
##############################
from odherogrid.cli.help import get_help_string
from odherogrid.cli.params import get_click_params
from odherogrid.cli.parse import (parse_arg_brackets,  # TODO: parse_config
                                  parse_arg_grouping)
from odherogrid.config import (CONFIG, CONFIG_BASE, _load_config,
                               check_config_integrity, update_config)
from odherogrid.enums import Brackets, Grouping
from odherogrid.error import get_stack_frames
from odherogrid.herogrid import (HeroGrid, HeroGridConfig,
                                 autodetect_steam_userdata_path,
                                 get_hero_grid_config_path)
from odherogrid.odapi import fetch_hero_stats
from odherogrid.odhg import main, parse_config


stats = None
N_HEROES = 119
TEST_CONFIG_PATH = "tests/testconf.yml"
TEST_HEROGRID_PATH = "tests/hero_grid_config.json"

# Ideally, this is a temporary workaround
# Replace with own hero_grid_config.json path if testing
if sys.platform == "win32":
    HERO_GRID_PATH = "C:/Program Files (x86)/Steam/userdata/19123403/570/remote/cfg/hero_grid_config.json"
elif sys.platform == "darwin":
    HERO_GRID_PATH = "/Users/Peder-MAC/Library/Application Support/Steam/userdata/19123403/570/remote/cfg/hero_grid_config.json"
elif sys.platform == "linux":
    raise NotImplementedError("Testing not yet implemented for Linux platforms")


def _get_hero_stats(sort: bool=False) -> List[dict]:
    global stats
    if stats is None:
        stats = fetch_hero_stats()
    if sort:
        return sort_heroes_by_winrate(stats, bracket=Brackets.DEFAULT.value)
    return stats


def _get_hero_wl(hero: dict, bracket: Brackets) -> float:
    return hero[f"{bracket.value}_win"] / hero[f"{bracket.value}_pick"]


@pytest.fixture(scope="module")
def heroes() -> List[dict]:
    return _get_hero_stats()


@pytest.fixture(scope="module")
def heroes_sorted() -> List[dict]:
    return _get_hero_stats(sort=True)


@pytest.fixture(scope="module")
def testconf() -> Path:
    testconf = Path(TEST_CONFIG_PATH)
    testgrid = Path(TEST_HEROGRID_PATH)
    # Copy the base config
    conf = deepcopy(CONFIG_BASE)
    # Copy hero grid to temp test directory
    shutil.copy(HERO_GRID_PATH, testgrid)
    conf["path"] = str(testgrid)
    # Save test config
    update_config(conf, filename=testconf)
    yield testconf
    testgrid.unlink()
    return testconf.unlink()


@pytest.fixture(scope="module")
def testconf_dict(testconf) -> dict:
    return _load_config(filename=testconf)


@pytest.fixture
def config_empty() -> dict:
    return deepcopy(CONFIG_BASE)


@pytest.fixture(scope="module")
def herogridconfig(heroes, testconf_dict) -> HeroGridConfig:
    return HeroGridConfig(heroes, testconf_dict)


# odhg.py
def test_parse_config():
    """
    NOTE: Requires a valid config. (Remove this?)
    """
    config = _load_config()
    config = parse_config(config)
    for v in config.values():
        assert v is not None


def test_get_help_string():
    """FIXME: Unfinished"""
    assert get_help_string()


def test_parameters():
    """Ensures parameters are properly added to odhg.main()"""
    for parameter in get_click_params():
        attrs = [
            "human_readable_name", "default", "name", 
            "nargs", "opts", "hidden", "is_flag", "is_bool_flag",
            "multiple",
        ]
        main_param = next(p for p in main.params if parameter.name == p.name)
        assert main_param
        for attr in attrs:
            assert getattr(parameter, attr) == getattr(main_param, attr)

# odapi.py
def test_opendota_api(heroes):
    """Tests type of data returned by `odhg.fetch_hero_stats()`"""
    
    # Ensure data returned by fetch_hero_stats() is a list
    assert isinstance(heroes, list)

    # Ensure all heroes are included
    assert len(heroes) == N_HEROES
    
    # Verify that all elements in heroes list are dicts
    assert all(isinstance(hero, dict) for hero in heroes)


# parseargs.py
def test_parse_arg_brackets_enum():
    """Tests every Enum Bracket value against `odhg.parse_brackets()`"""
    for b in [b for b in Brackets if b != Brackets.ALL]:
        assert parse_arg_brackets([str(b.value)]) == [b.value]
        assert parse_arg_brackets([b.value]) == [b.value]


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ##
        # list(set([1,6,7,8])) == [8, 1, 6, 7] on my computer, so to ensure
        # testing against correct expected values, all expected values are
        # converted to set then list.
        ##
        # Mix of ints, single chars and strings
        ([1, 6, "d", "pro"], list(set([1, 6, 7, 8]))),
        # 0 as arg
        ([0], list(set([1, 2, 3, 4, 5, 6, 7, 8]))),
        (["0"], list(set([1, 2, 3, 4, 5, 6, 7, 8]))),
        ([0, 1, 2, 3, 7], list(set([1, 2, 3, 4, 5, 6, 7, 8]))),
        # Duplicate arguments
        ([7, "d", "divine"], [7]),
        ([7, 7, 7], [7]),
        ]
)
def test_parse_arg_brackets_mixed(test_input, expected):
    """Tests different arguments and argument types."""
    assert parse_arg_brackets(test_input) == expected


def test_parse_arg_grouping():
    """Tests every Grouping value against `odhg.parse_brackets()`"""
    for g in Grouping:
        assert parse_arg_grouping(str(g.value)) == g.value
        assert parse_arg_grouping(g.name.lower()) == g.value


# herogrid.py
def test_get_cfg_path_nopath():
    """Tests userdata directory auto-detection."""
    assert autodetect_steam_userdata_path().exists()


@pytest.mark.skip(reason="Need to figure out a way to test this properly.")
def test_get_cfg_path():
    """Test with default config path"""
    assert get_hero_grid_config_path("SOMEPATH").exists()


def test_get_cfg_path_invalid():
    """Test with nonexistant path"""
    with pytest.raises(FileNotFoundError):
        assert get_hero_grid_config_path("notapath")


def test_get_cfg_path_none():
    """Test with nonexistant path"""
    with pytest.raises(TypeError) as e:
        assert get_hero_grid_config_path(None)
    assert e.exconly() == "TypeError: hero grid config path cannot be a None value!"





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
    herogridconfig.save_hero_grid_config(path=TEST_HEROGRID_PATH)

def _check_herogrid(name: str, grid: dict):
    # x in herogrid bla bla bla
    pass


# enums.py
def test_brackets_default():
    assert Brackets(Brackets.DEFAULT)


def test_grouping_default():
    assert Grouping(Grouping.DEFAULT)


def test_herogridconfig_create_grids(heroes, testconf_dict):
    conf = testconf_dict
    brackets = [b for b in Brackets if b != 0] # don't include ALL
    for bracket, grouping in itertools.product(brackets, Grouping):
        conf["brackets"] = [bracket]
        conf["grouping"] = grouping
        name = f"{bracket}{grouping}"
        conf["config_name"] = name
        h = HeroGridConfig(heroes, conf)
        h.create_grids()
        assert [
            c for c in h.hero_grid_config["configs"] 
            if c["config_name"] == f"{name} ({Brackets(bracket).name.capitalize()})"
            ][0]


def test_sort_heroes_by_winrate(heroes):
    """Tests `categorize.sort_heroes_by_winrate()`"""
    for bracket in [b for b in Brackets if b != Brackets.ALL]:
        heroes = sort_heroes_by_winrate(heroes, bracket=bracket.value)   
        for idx, hero in enumerate(heroes):
            try:
                next_hero = heroes[idx+1]
            except IndexError:
                break          
            assert _get_hero_wl(hero, bracket) >= _get_hero_wl(next_hero, bracket)


def test_group_by_main_stat(heroes_sorted):
    """Tests `categorize.group_by_main_stat()`"""
    categories = {
        "Strength": "str",
        "Agility": "agi",
        "Intelligence": "int"
    }
    conf = group_by_main_stat(heroes_sorted)
    
    # Test number of categories
    assert len(conf["categories"]) == 3
    
    # Test that heroes are in appropriate categories
    for category in conf["categories"]:
        for hid in category["hero_ids"]:
            for hero in heroes_sorted:
                if hero["id"] == hid:
                    assert hero["primary_attr"] == categories.get(category["category_name"])


def test_group_by_melee_ranged(heroes_sorted):
    """Tests `categorize.group_by_melee_ranged()`"""
    conf = group_by_melee_ranged(heroes_sorted)
    
    # Test number of categories
    assert len(conf["categories"]) == 2
    
    # Test that heroes are in appropriate categories
    for category in conf["categories"]:
        for hid in category["hero_ids"]:
            for hero in stats:
                if hero["id"] == hid:
                    assert hero["attack_type"] == category["category_name"]


def test_group_by_role(heroes_sorted):
    """Tests `categorize.group_by_role()`"""
    conf = group_by_role(heroes_sorted)
    
    # Test number of categories
    assert len(conf["categories"]) == 3
    
    # Test that heroes are in appropriate categories
    for category in conf["categories"]:
        for hid in category["hero_ids"]:
            for hero in heroes_sorted:
                if hero["id"] == hid:
                    if category["category_name"] == "Flexible":
                        assert "Carry" not in hero["roles"] and "Support" not in hero["roles"]
                    else:
                        assert category["category_name"] in hero["roles"]


def test_group_by_all(heroes_sorted):
    """Tests `categorize.group_by_all()`"""
    conf = group_by_all(heroes_sorted)

    # Test that there is only 1 category
    assert len(conf["categories"]) == 1

    # Test that all heroes are in the same category
    assert len(conf["categories"][0]["hero_ids"]) == N_HEROES


def test__get_new_category():
    arg = lambda: random.uniform(-3840, 3840)
    kwargs = ["x_pos", "y_pos", "width", "height"]
    for i in range(50):
        assert _get_new_category("test", x_pos=arg())
        assert _get_new_category("test", y_pos=arg())
        assert _get_new_category("test", width=arg())
        assert _get_new_category("test", height=arg())
        
        # Test random combination (and number) of keywords
        random.shuffle(kwargs)
        kw = kwargs[0:random.randint(1, len(kwargs))]
        params = {k: arg() for k in kw}
        assert _get_new_category("test", **params)


# config.py
def test_update_config(testconf):
    """Somewhat redundant, seeing as we use update_config in the fixture."""
    assert update_config(CONFIG_BASE, filename=testconf) is None


def test__load_config(testconf):
    for key in _load_config(filename=testconf):
        assert key in CONFIG_BASE


def test_check_config_integrity_default(monkeypatch, config_empty, testconf):
    """Tests check_config_integrity(), and chooses to replace missing keys
    with their default values."""
    for key in list(config_empty.keys()): # capture keys before modifying
        config_empty.pop(key)

        # replace with default value ("n" on  Y/n prompt)
        monkeypatch.setattr("sys.stdin", StringIO("n"))
        fixed = check_config_integrity(config_empty, filename=testconf)
        assert fixed == CONFIG_BASE


def test_check_config_integrity_userdefined(monkeypatch, config_empty, testconf):
    """Tests check_config_integrity(), and chooses to replace missing keys
    with custom values."""
    answers = {
        "brackets": "7",
        "config_name": "test",
        "grouping": "1",
        "path": "1",
        "sort": "1"
    }
    for key in list(config_empty.keys()): # capture keys before modifying
        config_empty.pop(key)
        
        # replace with custom value ("y" on Y/n prompt followed by desired choice)
        answer = answers.get(key)
        monkeypatch.setattr("sys.stdin", StringIO(f"y\n{answer}"))
        fixed = check_config_integrity(config_empty, filename=testconf)
        
        assert fixed.keys() == CONFIG_BASE.keys()


# errors.py
def test_get_stack_frames():
    assert next(get_stack_frames())
    for frame in get_stack_frames():
        assert frame

