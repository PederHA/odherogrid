__version__ = '0.2.0'

from .cli import *
from .config import *
from .enums import *
from .odapi import *
from .odhg import *
from .resources import *


CONFIG_NAME = "config.yml" # NOTE: Path("config.yml")?
CONFIG_DIR = Path().home() / ".odhg"
CONFIG = CONFIG_DIR / CONFIG_NAME 
