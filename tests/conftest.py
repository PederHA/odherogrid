import shutil
import sys
from copy import deepcopy
from pathlib import Path
from typing import List

import pytest

from odherogrid.config import CONFIG_BASE, _do_load_config, update_config
from odherogrid.herogrid import HeroGrid, HeroGridConfig
from odherogrid.odapi import fetch_hero_stats

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


@pytest.fixture
def N_HEROES() -> int:
    return 119


@pytest.fixture(scope="session")
def heroes() -> List[dict]:
    return fetch_hero_stats()


@pytest.fixture(scope="module")
def testconf(testconf_dict) -> Path:
    """Returns a path to a temporary test `config.yml`."""
    conf = Path(TEST_CONFIG_PATH)
    # Save test config
    update_config(testconf_dict, filename=conf)
    yield conf
    return conf.unlink()    


@pytest.fixture(scope="module")
def testgrid() -> Path:
    """Returns a mock of the contents expected in `hero_grid_config.json`."""
    grid = Path(TEST_HEROGRID_PATH)
    # Copy hero grid to temp test directory
    shutil.copy(HERO_GRID_PATH, grid)
    yield grid
    return grid.unlink()


@pytest.fixture(scope="module")
def testconf_dict(testgrid) -> dict:
    """Returns a mock of the contents expected in `config.yml`."""
    # Copy the base config
    testconf = deepcopy(CONFIG_BASE)
    testconf["path"] = TEST_HEROGRID_PATH
    return testconf


@pytest.fixture
def config_empty() -> dict:
    return deepcopy(CONFIG_BASE)


@pytest.fixture(scope="module")
def herogridconfig(heroes, testconf_dict) -> HeroGridConfig:
    return HeroGridConfig(heroes, testconf_dict)


@pytest.fixture
def herogrid(heroes, testconf_dict) -> HeroGrid:
    return HeroGrid(heroes, 7, testconf_dict)
