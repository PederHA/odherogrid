import pytest

from odherogrid.enums import Bracket, Layout, enum_start_end, enum_string


def test_brackets_default():
    assert Bracket(Bracket.DEFAULT)


def test_layout_default():
    assert Layout(Layout.DEFAULT)


@pytest.mark.parametrize("enum,expected_start,expected_end",
    [(Bracket, Bracket.ALL.value, Bracket.PRO.value),
     (Layout, Layout.SINGLE.value, Layout.ROLE.value)])
def test_enum_start_end(enum, expected_start, expected_end):
    start, end = enum_start_end(enum)
    assert start == expected_start
    assert end == expected_end


@pytest.mark.parametrize("enum", [Bracket, Layout])
def test_enum_string(enum):
    # Test number of lines
    lines = enum_string(enum).splitlines()
    assert len(lines) == len(enum)
    # Test contents of each line
    for line, e in zip(lines, enum):
        assert line.startswith(f"\t{e.value}.")

