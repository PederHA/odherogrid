from enum import IntEnum
from typing import Dict, List, Optional, Tuple, Union

import click

from ..enums import Brackets, Grouping
from ..herogrid import get_hero_grid_config_path


def make_mapping(mapping: Dict[Tuple[str], IntEnum]) -> Dict[Union[str, int], IntEnum]:
    """Make a new mapping with multiple keys for identical enums."""
    new = {}
    for keys, enum in mapping.items():
        new[enum.value] = enum.value         # add Enum value as key
        new[enum.name.lower()] = enum.value  # add Enum name as key
        for key in keys:
            new[key] = enum.value            # add existing keys from mapping
    return new


_brackets = {
    ("h",): Brackets.HERALD,
    ("g",): Brackets.GUARDIAN,
    ("c",): Brackets.CRUSADER,
    ("a",): Brackets.ARCHON,
    ("l",): Brackets.LEGEND,
    ("n",): Brackets.ANCIENT,
    ("d", "immortal", "i"): Brackets.DIVINE,
    ("p", "official", "tournaments"): Brackets.PRO,
    ("A", "all"): Brackets.ALL,
}

_grouping = {
    ("m", "stat", "mainstat", "stats"): Grouping.MAINSTAT,
    ("a", "melee", "range", "attack"): Grouping.ATTACK,
    ("r",): Grouping.ROLE,
    ("n", "all", "everything"): Grouping.NONE,
}


GROUPING = make_mapping(_grouping)
BRACKETS = make_mapping(_brackets)


def parse_arg_brackets(brackets: List[Union[str, int]]) -> List[int]:
    """Parses bracket (`-b` `--bracket`) argument.
    
    Returns list of integers.
    """
    # FIXME: this is a mess now

    # Check is Brackets.ALL is given as an argument
    if any(x in brackets for x in [str(Brackets.ALL.value), Brackets.ALL.value]):
        # Create list with all brackets
        valid_brackets = [b.value for b in Brackets if b.value != Brackets.ALL.value]
    else:
        # Parse arguments & make list of valid bracket arguments
        valid_brackets = list(
            filter(
                None.__ne__, [find_argument_in_mapping(b, BRACKETS) for b in brackets]
            )
        )

    # Fall back on default value if no valid brackets are provided
    if not valid_brackets:
        # TODO: raise ValueError?
        valid_brackets = [Brackets.DEFAULT.value]
        click.echo(
            "No valid bracket arguments provided. "
            f"Using default bracket: {Brackets.DEFAULT.name.capitalize()}"
        )

    return list(set(valid_brackets))


def parse_arg_grouping(grouping: str) -> int:
    """Parses grouping (`-g` `--group`) argument.
    
    Returns integer
    """
    grp = find_argument_in_mapping(grouping, GROUPING)
    if grp is None:
        # TODO: raise ValueError?
        grp = Grouping.DEFAULT.value
        click.echo(
            "No valid grouping arguments provided. "
            f"Using default bracket: {Grouping.DEFAULT.name.capitalize()}"
        )
    return grp


def find_argument_in_mapping(argument: Union[str, int], mapping: dict) -> Optional[int]:
    if isinstance(argument, str) and argument.isdigit():
        argument = int(argument)
    return mapping.get(argument)  # None is default


def parse_config(config: dict) -> dict:
    config["brackets"] = parse_arg_brackets(config["brackets"])
    config["grouping"] = parse_arg_grouping(config["grouping"])
    
    # We can fall back on bracket and grouping defaults
    # But we can't fall back on a default Steam userdata directory path
    try:
        config["path"] = get_hero_grid_config_path(config["path"]) # Steam userdata directory
    except (TypeError, ValueError) as e:
        click.echo(e.args[0])
        click.echo(
            "Either specify a valid path using the '--path' option, "
            "or run setup using the '--setup' flag to permanently add "
            "a valid path to your config."
        )
        raise SystemExit
    return config