"""Not to be confused with the argparse module in the Python standard library.
You can easily tell the difference, because this module is a piece of shit.
"""

from enum import Enum
from typing import List, Optional, Union

import click

from config import _parse_user_bracket_input
from enums import Brackets, Grouping


def make_mapping(mapping: dict) -> dict:
    """Make a new mapping with multiple keys for the same values."""
    new = {}
    for keys, value in mapping.items():
        new[value.value] = value.value
        new[value.name.lower()] = value.value
        for key in keys:
            new[key] = value.value
    return new


DEFAULT_BRACKET = Brackets.DIVINE
DEFAULT_GROUPING = Grouping.MAINSTAT


_brackets = {
    ("h",) : Brackets.HERALD,
    ("g",) : Brackets.GUARDIAN,
    ("c",) : Brackets.CRUSADER,
    ("a",) : Brackets.ARCHON,
    ("l",) : Brackets.LEGEND,
    ("n",) : Brackets.ANCIENT,
    ("d", "immortal", "i") : Brackets.DIVINE,
    ("p", "official", "tournaments") : Brackets.PRO,
    ("A",) : Brackets.ALL
}

_grouping = {
    ("m", "stat", "mainstat", "stats") : Grouping.MAINSTAT,
    ("a", "melee", "range", "attack") : Grouping.ATTACK,
    ("r",) : Grouping.ROLE,
    ("A", "N", "none", "all", "everything") : Grouping.NONE
}


GROUPING = make_mapping(_grouping)
BRACKETS = make_mapping(_brackets)



def parse_arg_brackets(brackets: List[Union[str, int]]) -> List[int]:
    """Parses bracket (`-b` `--bracket`) argument.
    
    Returns list of integers.
    """
    valid_brackets = list(
        filter(
            None.__ne__, 
            [find_argument_in_mapping(b, BRACKETS) for b in brackets]
        )
    )
    
    # Fall back on default value if no valid brackets are provided
    if not valid_brackets:
        valid_brackets = [DEFAULT_BRACKET.value]
        click.echo("No valid bracket arguments provided. "
                  f"Using default bracket: {DEFAULT_BRACKET.name.capitalize()}")
    # Check is Brackets.ALL is given as an argument
    elif Brackets.ALL.value in valid_brackets:
        valid_brackets = [
            b.value for b in Brackets if b.value != Brackets.ALL.value
            ]
    return valid_brackets


def parse_arg_grouping(grouping: str) -> int:
    """Parses grouping (`-g` `--group`) argument.
    
    Returns integer
    """
    grp = find_argument_in_mapping(grouping, GROUPING)
    if not grp:
        grp = DEFAULT_GROUPING.value
        click.echo("No valid grouping arguments provided. "
                  f"Using default bracket: {DEFAULT_GROUPING.name.capitalize()}")        
    return grp


def find_argument_in_mapping(argument: Union[str, int], mapping: dict) -> Optional[int]:
    if isinstance(argument, str) and argument.isdigit():
        argument = int(argument)
    
    return mapping.get(argument) # None is default
