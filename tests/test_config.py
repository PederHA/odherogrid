from io import StringIO

import pytest

from odherogrid.config import (CONFIG_BASE, _do_load_config,
                               check_config_integrity, update_config)


# config.py
def test_update_config(testconf, testconf_dict):
    """Somewhat redundant, seeing as we use update_config in the fixture."""
    assert update_config(testconf_dict, filename=testconf) is None


def test__do_load_config(testconf, testconf_dict):
    """Tests that all keys and values expected in `config.yml` are loaded properly."""
    c = _do_load_config(filename=testconf)
    for k, v in c.items():
        assert k in testconf_dict
        assert testconf_dict[k] == v


def test_check_config_integrity_default(monkeypatch, config_empty, testconf):
    """Tests check_config_integrity(), and chooses to replace missing keys
    with their default values."""
    conf = config_empty
    for key in list(conf.keys()): # capture keys before modifying
        conf.pop(key)

        # replace with default value ("n" on  Y/n prompt)
        monkeypatch.setattr("sys.stdin", StringIO("n"))
        conf = check_config_integrity(conf, filename=testconf)
        assert conf == CONFIG_BASE


def test_check_config_integrity_userdefined(monkeypatch, config_empty, testconf):
    """Tests check_config_integrity(), and chooses to replace missing keys
    with custom values."""
    answers = {
        "brackets": "7",
        "config_name": "test",
        "layout": "1",
        "path": "1",
        "ascending": "1"
    }
    conf = config_empty
    for key in list(conf.keys()): # capture keys before modifying
        conf.pop(key)
        
        # replace with custom value ("y" on Y/n prompt followed by desired choice)
        answer = answers.get(key)
        monkeypatch.setattr("sys.stdin", StringIO(f"y\n{answer}"))
        conf = check_config_integrity(conf, filename=testconf)
        
        assert conf.keys() == CONFIG_BASE.keys()
