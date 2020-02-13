import pytest

from odherogrid.cli.parse import parse_arg_brackets, parse_arg_layout, parse_config
from odherogrid.cli.help import get_help_string
from odherogrid.cli.params import get_click_params
from odherogrid.enums import Bracket, Layout
from odherogrid.odhg import main

def test_parse_arg_brackets_enum():
    """Tests every Enum Bracket value against `odhg.parse_brackets()`"""
    for b in [b for b in Bracket if b != Bracket.ALL]:
        assert parse_arg_brackets([str(b.value)]) == [b.value]
        assert parse_arg_brackets([b.value]) == [b.value]


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Mix of ints, single chars and strings
        ([1, 6, "d", "pro"], list(set([1, 6, 7, 8]))),
        # 0 as arg
        ([0], list(set([1, 2, 3, 4, 5, 6, 7, 8]))),
        (["0"], list(set([1, 2, 3, 4, 5, 6, 7, 8]))),
        ([0, 1, 2, 3, 7], list(set([1, 2, 3, 4, 5, 6, 7, 8]))),
        # Duplicate arguments
        ([7, "d", "divine"], [7]),
        ([7, 7, 7], [7]),
    ]
)
def test_parse_arg_brackets_mixed(test_input, expected):
    """Tests different arguments and argument types."""
    assert parse_arg_brackets(test_input) == expected


def test_parse_arg_layout():
    """Tests every Layout value against `odhg.parse_brackets()`"""
    for g in Layout:
        assert parse_arg_layout(str(g.value)) == g.value
        assert parse_arg_layout(g.name.lower()) == g.value


def test_parse_config(testconf_dict):
    """
    NOTE: Requires a valid config. (Remove this?)
    """
    config = parse_config(testconf_dict)
    for v in config.values():
        assert v is not None


def test_get_help_string():
    """FIXME: Unfinished"""
    assert get_help_string()


def test_parameters():
    """Ensures parameters are properly added to odhg.main()"""
    for parameter in get_click_params():
        attrs = [
            "human_readable_name", "default", "name", 
            "nargs", "opts", "hidden", "is_flag", "is_bool_flag",
            "multiple",
        ]
        main_param = next(p for p in main.params if parameter.name == p.name)
        assert main_param
        for attr in attrs:
            assert getattr(parameter, attr) == getattr(main_param, attr)