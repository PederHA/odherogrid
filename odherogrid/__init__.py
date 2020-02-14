from pathlib import Path

__version__ = '0.2.0'

CONFIG_NAME = "config.yml" # NOTE: Path("config.yml")?
CONFIG_DIR = Path().home() / ".odhg"
CONFIG = CONFIG_DIR / CONFIG_NAME 

from .cli import *
from .config import *
from .enums import *
from .odapi import *
from .odhg import *
from .resources import *


