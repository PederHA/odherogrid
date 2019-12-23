import sys
from pathlib import Path
from typing import List, Union

import click
import yaml

from .cfg import _get_steam_userdata_path
from .enums import Brackets, Grouping
from .parseargs import parse_arg_brackets

CONF = "config.yml" # NOTE: Path("config.yml")?

CONFIG_BASE = {
    "path": None,
    "brackets": [Brackets.DEFAULT.value],
    "grouping": Grouping.DEFAULT.value,
    "config_name": "OpenDota Hero Winrates",
    "sort": "desc"
}


def _load_config(*, filename: str=None) -> dict:
    """Loads configuration file and returns it as a dict."""
    path = filename or CONF
    with open(path, "r") as f:
        config = yaml.load(f.read(), Loader=yaml.loader.FullLoader)
    if not config:
        raise ValueError
    return config


def load_config() -> dict:
    """Attempts to load configuration file. 
    If it does not exist, user is prompted to run first time setup.

    TODO: Should config["steam"]["path"] be a Path object?
    """
    try:
        config = _load_config()
    except (FileNotFoundError, ValueError):
        if click.confirm(
            "Could not find ODHG config! Do you want to run first time setup?"
            ):
            config = run_first_time_setup()
        else:
            raise SystemExit("Exiting.")
    
    # Ensure all necessary config keys are present
    config = _check_config_integrity(config)

    return config


def update_config(config: dict, *, filename: str=None) -> None:
    """Saves config as a YAML file."""
    path = filename or CONF
    with open(path, "w") as f:
        f.write(yaml.dump(config, default_flow_style=False))    


def _check_config_integrity(config: dict) -> dict:
    CONFIG_FUNCS = {
        "path": setup_userdata_cfg_dir,
        "brackets": setup_bracket,
        "grouping": setup_grouping,
        "config_name": setup_config_name,
        "sort": setup_winrate_sorting
    }

    # Remove unknown keys
    for key in config:
        if key not in CONFIG_BASE:
            config.pop(key)

    # Check for missing keys
    missing_keys = [(k, v) for (k, v) in CONFIG_BASE.items() if k not in config]
    if missing_keys:
        missing = ", ".join([key for (key, value) in missing_keys])
        click.echo(f"'config.yml' is missing the following keys: {missing}")

        # Replace missing keys in user's config
        for (key, value) in missing_keys:
            func = CONFIG_FUNCS.get(key)
            # TODO: add missing config_func handling?
            if click.confirm(
                f"Do you want add a value for the missing key '{key}'?"
                ):
                config = func(config)
            else:
                config[key] = value
                click.echo("Adding missing key with default value.")
        
        update_config(config)

    return config


def get_path_from_user() -> Path:
    """Gets a valid path from user input."""
    p = click.prompt("Path: ")
    while not Path(p).exists():
        click.echo("Path does not exist.")
        p = click.prompt("Provide an existing path or type 'q' to quit.")
        if p.lower() == "q":
            raise SystemExit("Quitting.")
    return p


def ask_steam_userdata_path() -> Path:
    if click.confirm("Would you like to specify your userdata directory manually?"):
        click.echo("\nIt should look something like this: ", nl=False)
        
        # Per-platform message
        if sys.platform == "win32":
            click.echo("'C:\\Program Files (x86)\\Steam\\userdata\\<ID>")
        elif sys.platform == "darwin":
            click.echo("~/Library/Application Support/Steam/userdata/<ID>")
        elif sys.platform == "linux":
            click.echo("~/Steam/userdata/<ID>")
        
        return get_path_from_user()
    else:
        raise SystemExit("Unable to locate Steam userdata directory.") # abort


def setup_userdata_cfg_dir(config: dict) -> dict:
    """Configure user's Dota userdata cfg directory.
    """
    # Get default directory for Steam userdata
    click.echo("\nSteam Userdata Directory:")
    try:
        p = _get_steam_userdata_path()
    except NotImplementedError as e:
        click.echo(e.args[0])
        cfg_path = ask_steam_userdata_path()
    else:
        directories = [d for d in p.iterdir()]
        
        # Ask user for a path if no directories found in auto-detected path
        if not directories:
            click.echo(f"No subdirectories were found in {p}")
            cfg_path = ask_steam_userdata_path()
        
        else:
            # Subdirectories
            subdirs = {idx+1: d for idx, d in enumerate(directories)}
            
            # Let user select a directory
            _choices = "\n".join(f"\t{idx}. {d.stem}" for idx, d in subdirs.items())
            click.echo(_choices)
            
            choice = 0
            while choice not in subdirs:
                choice = click.prompt(f"Select directory (1-{len(directories)})", type=int) 
            cfg_path = subdirs.get(choice)
    finally:    
        config["path"] = str((cfg_path / "570/remote/cfg"))
    
    return config


def setup_bracket(config: dict) -> dict:
    # Determine lowest and highest Bracket enum value
    _b_values = [b.value for b in Brackets]
    brackets_start = min(_b_values)
    brackets_end = max(_b_values)
    
    # Prompt user to select a default bracket
    available_brackets = get_enum_string(Brackets)
    click.echo(f"\nBrackets:\n{available_brackets}")

    brackets = _get_brackets(
        "Specify default skill bracket(s), separated by spaces", 
        brackets_start, 
        brackets_end
    )
    while not brackets:
        brackets = _get_brackets(
            "No valid brackets provided. Try again", 
            brackets_start, 
            brackets_end
        )

    config["brackets"] = brackets

    return config


def _get_brackets(msg: str, brackets_start: int, brackets_end: int) -> List[int]:
    b = click.prompt(
        f"{msg} ({brackets_start}-{brackets_end})",
        type=str,
        default=str(Brackets.DEFAULT.value),
        show_default=False
    )
    return parse_arg_brackets(b.split(" "))


def setup_grouping(config: dict) -> dict:
    # Determine lowest and highest Grouping enum value
    _g_values = [g.value for g in Grouping]
    grouping_start = min(_g_values)
    grouping_end = max(_g_values)
    
    # Prompt user to select a default grouping
    click.echo(get_enum_string(Grouping))

    
    get_grp = lambda m: click.prompt(
        f"{m} ({grouping_start}-{grouping_end})",
        type=int,
        default=Grouping.DEFAULT.value,
        show_default=False
    )  
    grouping = get_grp("\nSelect default hero grouping") 
    while grouping not in _g_values:
        grouping = get_grp("Invalid grouping. Try again")
    
    config["grouping"] = grouping

    return config


def get_enum_string(enum: Union[Brackets, Grouping]) -> str:
    choices = "\n".join(
        f"\t{e.value}. {e.name.capitalize()}" 
        if e != enum.DEFAULT else 
        f"\t{e.value}. {e.name.capitalize()} [default]" 
        for idx, e in enumerate(enum)
    )
    return choices


def setup_config_name(config: dict) -> dict:
    """Setup for default name of hero grid."""
    click.echo(
        f"\nChoose a default hero grid name. (current: {config['config_name']})"
        )
    name = click.prompt(
        f"New name (leave blank to keep current name)", 
        default="",
        show_default=False
        )
    if name:
        config["config_name"] = name
    return config


def setup_winrate_sorting(config: dict) -> dict:
    click.echo("\nDo you want to sort heroes by winrates descending or ascending?")
    click.echo("1. Descending [default]")
    click.echo("2. Ascending")
    
    choice = 0
    while choice not in [1, 2]:
        choice = click.prompt("Choice (1-2)", type=int, default=1, show_default=False)
    config["sort"] = (choice == 1)

    return config


def run_first_time_setup() -> dict:
    # Create new config file
    p = Path(CONF)
    if Path(CONF).exists():
        if not click.confirm(
            f"'{p}' already exists. Are you sure you want to overwrite it?"
        ):
            click.echo("Aborting setup.")
            raise SystemExit
    
    click.echo("Creating new config...")  
    config = CONFIG_BASE

    # Setup config parameters
    config = setup_userdata_cfg_dir(config)
    config = setup_bracket(config)
    config = setup_grouping(config)
    config = setup_winrate_sorting(config)
    config = setup_config_name(config)

    update_config(config)

    return config
