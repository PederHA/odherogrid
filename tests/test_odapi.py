def test_opendota_api_type(heroes):
    # Ensure data returned by fetch_hero_stats() is a list
    assert isinstance(heroes, list)


def test_opendota_api_count(heroes, N_HEROES):
    # Ensure all heroes are included
    assert len(heroes) == N_HEROES


def test_opendota_api_contents(heroes, N_HEROES):
    # Verify that all elements in heroes list are dicts
    assert all(isinstance(hero, dict) for hero in heroes)
