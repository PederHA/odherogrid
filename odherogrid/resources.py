from copy import deepcopy

DEFAULT_NAME = "OpenDota Hero Winrates"


CATEGORY_BASE = {
    "category_name": "name",
    "x_position": 0.000000,
    "y_position": 0.000000,
    "width": 1180.0,
    "height": 180.0,
    "hero_ids": [],
}


HERO_GRID_BASE = {
    "config_name": DEFAULT_NAME,
    "categories": [
        {
            "category_name": "Strength",
            "x_position": 0.000000,
            "y_position": 0.000000,
            "width": 1180.0,
            "height": 180.0,
            "hero_ids": [],
        },
        {
            "category_name": "Agility",
            "x_position": 0.000000,
            "y_position": 200.000000,
            "width": 1180.0,
            "height": 180.0,
            "hero_ids": [],
        },
        {
            "category_name": "Intelligence",
            "x_position": 0.000000,
            "y_position": 400.000000,
            "width": 1180.0,
            "height": 180.0,
            "hero_ids": [],
        }
    ]
}


HERO_GRID_CONFIG_BASE = {
    "version": 3,
    "configs": [
        deepcopy(HERO_GRID_BASE)
    ],
}

# Represents default hero_grid_config.json
CONFIG_BASE = {
    "version": 3,
    "configs": [],
}

def _get_new_category(name: str, x_pos: float=0.0, y_pos: float=0.0, width: float=0.0, height: float=0.0) -> dict:
    # Copy category and give it a name
    category = deepcopy(CATEGORY_BASE)
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


def get_new_hero_grid_base() -> dict:
    return deepcopy(HERO_GRID_BASE)


def get_new_hero_grid_config() -> dict:
    return deepcopy(CONFIG_BASE)