"""
This module implements functionality related to generating, maintaining
and updating a persistent user configuration file for ODHeroGrid. 
"""

import sys
from copy import deepcopy
from pathlib import Path
from typing import List, Union

import click
import yaml

from .cli.parse import parse_arg_brackets
from .cli.utils import progress
from .enums import Bracket, Layout, enum_start_end, enum_string
from .herogrid import detect_userdata_path
from .settings import DEFAULT_GRID_NAME, CONFIG
from .error import handle_exception


CONFIG_BASE = {
    "path": None,
    "brackets": [Bracket.DEFAULT.value],
    "layout": Layout.DEFAULT.value,
    "config_name": DEFAULT_GRID_NAME,
    "ascending": False,
}


def _do_load_config(*, filename: Union[str, Path]=None) -> dict:
    """Loads configuration file and returns it as a dict."""
    path = filename or CONFIG
    with open(path, "r") as f:
        config = yaml.load(f.read(), Loader=yaml.loader.FullLoader)
    if not config:
        if click.confirm(
            "Config is empty or damaged! "
            "Do you want to attempt to repair it?"
        ):
            return check_config_integrity(config)
        else:
            raise SystemExit("Cannot proceed with the current config! Exiting.")
    return config


def load_config() -> dict:
    """Attempts to load configuration file. 
    If it does not exist, user is prompted to run first time setup.

    TODO: Should config["steam"]["path"] be a Path object?
    """
    try:
        config = _do_load_config()
    except (FileNotFoundError, ValueError):
        if click.confirm(
            "Could not find ODHG config! Do you want to run first time setup?"
            ):
            config = run_first_time_setup()
        else:
            raise SystemExit("Exiting.")
    
    # Ensure all necessary config keys are present
    config = check_config_integrity(config)

    return config


def create_config(config: dict, *, filename: Union[str, Path]=None) -> None:
    """Creates a config file and its parent directories (if needed)"""
    path = Path((filename or CONFIG))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    except Exception as e:  # We are mainly concerned with OSError and its
        handle_exception(e) # subclasses, but we might as well log all errors here.
        


def update_config(config: dict, *, filename: Union[str, Path]=None) -> None:
    """Saves config as a YAML-formatted file."""
    path = Path((filename or CONFIG)) # make sure we have a path object
    if not path.exists():
        create_config(config, filename=filename)
    with open(path, "w") as f:
        f.write(yaml.dump(config, default_flow_style=False))    


def check_config_integrity(config: dict, *, filename: Union[str, Path]=None) -> dict:
    """Removes unknown keys and inserts missing keys."""
    # Remove unknown keys
    c = deepcopy(config) # config copy so we can modify while iterating
    for key in config:
        if key not in CONFIG_BASE:
            c.pop(key)
    config = c

    # Check for missing keys
    missing_keys = [(k, v) for (k, v) in CONFIG_BASE.items() if k not in config]
    if missing_keys:
        _fix_missing_keys(config, missing_keys)
        update_config(config, filename=filename)
    
    return config


def _fix_missing_keys(config: dict, missing_keys: list) -> dict:
    CONFIG_FUNCS = {
        "path": setup_hero_grid_config_path,
        "brackets": setup_bracket,
        "layout": setup_layout,
        "config_name": setup_config_name,
        "ascending": setup_winrate_sorting
    }

    missing = ", ".join([key for (key, value) in missing_keys])
    click.echo(f"'config.yml' is missing the following keys: {missing}")

    # Replace missing keys in user's config
    # TODO: Improve prompt. 
    #       Reinforce that choosing "no" replaces with default val
    for (key, value) in missing_keys:
        if click.confirm(
            f"Do you want add a value for the missing key '{key}'?"
        ):
            func = CONFIG_FUNCS.get(key)
            if not func:
                raise KeyError(
                    f"No function exists to fill config entry '{key}'! "
                    "Report this bug!"
                    )
            config = func(config)
        else:
            config[key] = value
            click.echo("Adding missing key with default value.")

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


def setup_hero_grid_config_path(config: dict) -> dict:
    """Configure user's Dota userdata cfg directory.
    """
    # Get default directory for Steam userdata
    click.echo("Steam Userdata Directory:")
    try:
        p = detect_userdata_path()
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
        config["path"] = str((cfg_path / "570/remote/cfg/hero_grid_config.json"))
    
    return config


def setup_bracket(config: dict) -> dict:
    # Determine lowest and highest Bracket enum value
    brackets_start, brackets_end = enum_start_end(Bracket)

    # Prompt user to select a default bracket
    available_brackets = enum_string(Bracket)
    click.echo(f"Bracket:\n{available_brackets}")

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
        default=str(Bracket.DEFAULT.value),
        show_default=False
    )
    return parse_arg_brackets(b.split(" "))


def setup_layout(config: dict) -> dict:
    # Prompt user to select a default layout
    available_layout = enum_string(Layout)
    click.echo(f"Layout:\n{available_layout}")

    # Determine lowest and highest Layout enum value
    layout_start, layout_end = enum_start_end(Layout)
    g_range = list(range(layout_start, layout_end+1))
    
    get_grp = lambda m: click.prompt(
        f"{m} ({layout_start}-{layout_end})",
        type=int,
        default=Layout.DEFAULT.value,
        show_default=False
    )  
    layout = get_grp("Select default hero layout") 
    while layout not in g_range:
        layout = get_grp("Invalid layout. Try again")
    
    config["layout"] = layout

    return config


def setup_config_name(config: dict) -> dict:
    """Setup for default name of hero grid."""
    click.echo(
        f"Default hero grid name. (default: {DEFAULT_GRID_NAME})"
    )
    name = click.prompt(
        f"Name", 
        default=DEFAULT_GRID_NAME,
        show_default=False
    )
    if name:
        config["config_name"] = name
    return config


def setup_winrate_sorting(config: dict) -> dict:
    click.echo("Winrate sorting")
    click.echo("1. Descending [default]") # TODO: don't harcode "[default]"
    click.echo("2. Ascending")
    
    choice = 0
    while choice not in [1, 2]:
        choice = click.prompt("Choice (1-2)", type=int, default=1, show_default=False)
    config["ascending"] = (choice == 1)

    return config


def run_first_time_setup() -> dict:
    # Create new config file
    if CONFIG.exists():
        if not click.confirm(
            f"'{CONFIG}' already exists. Are you sure you want to overwrite it?"
        ):
            click.echo("Aborting setup.")
            raise SystemExit
    
    with progress("Creating new config...", success="Config created ✔️",nl=False):
        return _do_run_first_time_setup()


def _do_run_first_time_setup() -> dict:
    config = deepcopy(CONFIG_BASE)

    # Setup config parameters
    functions = [
        setup_hero_grid_config_path,
        setup_bracket,
        setup_layout,
        setup_winrate_sorting,
        setup_config_name
    ]
    # NOTE: I could have done some bullshit with globals()
    #       and startswith("setup_"), but let's keep it simple

    with click.progressbar(functions, bar_template="[%(bar)s]  %(info)s") as bar:
        click.clear()
        for func in bar:
            click.echo("\n") # newline after displaying progress bar
            config = func(config)
            click.clear()
    
    update_config(config)

    return config
