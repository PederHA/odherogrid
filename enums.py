from enum import Enum

class Brackets(Enum):
    ALL = 0
    HERALD = 1
    GUARDIAN = 2
    CRUSADER = 3
    ARCHON = 4
    LEGEND = 5
    ANCIENT = 6
    DIVINE = 7
    PRO = 8


class Grouping(Enum):
    ALL = 0
    MAINSTAT = 1
    ATTACK = 2
    ROLE = 3