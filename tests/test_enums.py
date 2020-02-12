import pytest

from odherogrid.enums import Brackets, Grouping, enum_start_end, enum_string


def test_brackets_default():
    assert Brackets(Brackets.DEFAULT)


def test_grouping_default():
    assert Grouping(Grouping.DEFAULT)


@pytest.mark.parametrize("enum,expected_start,expected_end",
    [(Brackets, Brackets.ALL.value, Brackets.PRO.value),
     (Grouping, Grouping.NONE.value, Grouping.ROLE.value)])
def test_enum_start_end(enum, expected_start, expected_end):
    start, end = enum_start_end(enum)
    assert start == expected_start
    assert end == expected_end


@pytest.mark.parametrize("enum", [Brackets, Grouping])
def test_enum_string(enum):
    # Test number of lines
    lines = enum_string(enum).splitlines()
    assert len(lines) == len(enum)
    # Test contents of each line
    for line, e in zip(lines, enum):
        assert line.startswith(f"\t{e.value}.")

