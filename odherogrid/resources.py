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


CONFIG_BASE = {
    "version": 3,
    "configs": [],
}
