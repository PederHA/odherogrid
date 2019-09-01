import pytest

from odhg import Brackets, get_hero_stats, sort_heroes_by_winrate, get_brackets, get_cfg_path

PATH = r"C:\Program Files (x86)\Steam\userdata\19123403\570\remote\cfg"
stats = None

def _get_stats():
    global stats
    if stats is None:
        stats = get_hero_stats()
    return stats


def _get_hero_wl(hero: dict, bracket: Brackets) -> float:
    return hero[f"{bracket.value}_win"] / hero[f"{bracket.value}_pick"]


def test_winrate_sorting():
    heroes = _get_stats()
    for bracket in [b for b in Brackets if b != Brackets.ALL]:
        heroes = sort_heroes_by_winrate(heroes, bracket=bracket.value)
        
        for idx, hero in enumerate(heroes):
            try:
                next_hero = heroes[idx+1]
            except IndexError:
                break
                    
            assert _get_hero_wl(hero, bracket) >= _get_hero_wl(next_hero, bracket)


def test_opendota_api_type():
    heroes = _get_stats()
    assert isinstance(heroes, list)


def test_opendota_api_contents():
    heroes = _get_stats()
    assert all(isinstance(hero, dict) for hero in heroes)


def test_get_brackets():
    brackets = [b for b in Brackets if b != Brackets.ALL]
    for b in brackets:
        assert get_brackets(str(b.value)) == [b.value]


def test_get_cfg_path_nopath():
    assert get_cfg_path(None).exists()


def test_get_cfg_path_withpath():
    assert get_cfg_path(PATH).exists()


def test_get_cfg_path_invalid_path():
    with pytest.raises(ValueError):
        assert get_cfg_path("notapath")
