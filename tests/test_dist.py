from pathlib import Path

import toml

from odherogrid import __version__


ODHG_ROOT = Path(__file__).parent.parent # same as var in scripts/resouces.py
with open(ODHG_ROOT/"pyproject.toml") as f:
    pyproject = toml.load(f)


def test_version():
    assert __version__ == pyproject["tool"]["poetry"]["version"] == "0.3.0"
