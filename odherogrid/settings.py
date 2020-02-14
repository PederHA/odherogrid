from pathlib import Path

CONFIG_NAME = "config.yml" # NOTE: Path("config.yml")?
CONFIG_DIR = Path().home() / ".odhg"
CONFIG = CONFIG_DIR / CONFIG_NAME

DEFAULT_GRID_NAME = "OpenDota Hero Winrates"
