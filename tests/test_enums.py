from odherogrid.enums import Brackets, Grouping


def test_brackets_default():
    assert Brackets(Brackets.DEFAULT)


def test_grouping_default():
    assert Grouping(Grouping.DEFAULT)