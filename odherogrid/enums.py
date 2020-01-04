from enum import IntEnum


class Brackets(IntEnum):
    ALL = 0
    HERALD = 1
    GUARDIAN = 2
    CRUSADER = 3
    ARCHON = 4
    LEGEND = 5
    ANCIENT = 6
    DIVINE = 7
    PRO = 8
    
    # default bracket
    DEFAULT = DIVINE


class Grouping(IntEnum):
    NONE = 0
    MAINSTAT = 1
    ATTACK = 2
    ROLE = 3

    # default grouping (Standard Dota 2 hero grid [str, int, agi])
    DEFAULT = MAINSTAT


def enum_string(enum: IntEnum) -> str:
    choices = "\n".join(
        f"\t{e.value}. {e.name.capitalize()}" 
        if e != enum.DEFAULT else 
        f"\t{e.value}. {e.name.capitalize()} [default]" 
        for e in enum
    )
    return choices