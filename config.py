from pathlib import Path

import click
import yaml

from enums import Brackets, Grouping
from cfg import _get_steam_userdata_path


CONF = "config.yml"

CONFIG_BASE = {
    "path": None,
    "brackets": [Brackets.DIVINE.value],
    "grouping": Grouping.MAINSTAT.value,
    "config_name": "OpenDota Hero Winrates",
    "sort": "desc"
}


def _load_config() -> dict:
    """Loads configuration file and returns it as a dict."""
    with open(CONF, "r") as f:
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


def _check_config_integrity(config: dict) -> dict:
    # Check for missing keys
    missing_keys = []
    for key, value in CONFIG_BASE.items():
        if key not in config:
            missing_keys.append((key, value))
    
    # Remove unknown keys
    for key in config:
        if key not in CONFIG_BASE:
            config.pop(key) # remove unknown key

    if missing_keys:
        first = True
        click.echo("'config.yml' is lacking the following keys: ", nl=False)
        for (key, value) in missing_keys:
            if not first:
                click.echo(", ", nl=False)
            else:
                first = False
            click.echo(key, nl=False)
        click.echo(".")
        click.echo("Adding missing keys.")
        
        # Replace missing keys
        for (key, value) in missing_keys:
            config[key] = value
        
        update_config(config)

    return config


def update_config(config: dict) -> None:
    """Updates config file."""
    _dump_config(Path(CONF), config)


def _dump_config(path: Path, config: dict) -> None:
    """Function to be used by any other functions that want to modify
    the config file."""
    with open(path, "w") as f:
        f.write(yaml.dump(config, default_flow_style=False))    


def remake_config() -> None:
    """Unused"""
    p = Path("config.yml")
    try:
        p.unlink()
    except FileNotFoundError:
        click.echo("Config.yml does not exist!")
        if not click.confirm("Do you want to run first time setup to create a config?"):
            return
    else:
        click.echo("Running first time setup.")       
    finally:
        config = run_first_time_setup()
        update_config(config)
        click.echo("Successfully remade config!")


def get_path_from_user() -> Path:
    """Gets a valid path from user input."""
    p = click.prompt("Path: ")
    while not Path(p).exists():
        click.echo("Path does not exist.\n")
        p = click.prompt("Provide an existing path or type 'q' to quit.")
        if p.lower() == "q":
            raise SystemExit("Quitting.")
    return p


def setup_userdata_cfg_dir(config: dict) -> dict:
    """This is a little janky."""
    # Get default directory for Steam userdata
    p = _get_steam_userdata_path()
    
    directories = [d for d in p.iterdir()]
    if not directories:
        click.echo(f"No subdirectories were found in {p}")
        if click.confirm("Would you like to specify the userdata directory manually?"):
            click.echo("\nIt should look something like this: "
            "'C:\\Program Files (x86)\\Steam\\userdata\\<ID>\\570\\remote\cfg'.")
            cfg_path = get_path_from_user()
        else:
            raise SystemExit("Unable to locate Steam userdata directory.") # abort
    
    else:
        # Subdirectories
        subdirs = {idx+1: d for idx, d in enumerate(directories)}
        
        # Let user select a directory
        _choices = "\n".join(f"{idx}. {d.stem}" for idx, d in subdirs.items())
        click.echo(_choices)
        
        choice = 0
        while choice not in subdirs:
            choice = click.prompt(f"Select directory (1-{len(directories)})", type=int)
        
        cfg_path = subdirs.get(choice)
        
    config["path"] = str((cfg_path / "570/remote/cfg"))
    
    return config


def setup_bracket(config: dict) -> dict:
    # Determine lowest and highest Bracket enum value
    _b_values = [b.value for b in Brackets]
    brackets_start = min(_b_values)
    brackets_end = max(_b_values)
    
    # Prompt user to select a default bracket
    brackets = "\n".join(f"{b.value}. {b.name.capitalize()}" for idx, b in enumerate(Brackets))
    click.echo(brackets)  
    def_brackets = click.prompt(
        f"Specify default skill bracket(s), separated by spaces ({brackets_start}-{brackets_end})",
        type=str
        )
    
    # Parse user input
    valid = _parse_user_bracket_input(def_brackets)
    while not valid:
        click.prompt(
            f"No valid brackets provided. Try again ({brackets_start}-{brackets_end})",
            type=str
            )
        _parse_user_bracket_input(def_brackets)
    

    # TODO: Select multiple brackets
    
    config["brackets"] = valid

    return config


def _parse_user_bracket_input(inp: str) -> None:
    valid = []
    invalid = []
    for bracket in inp.split(" "):
        try:
            b = int(bracket)
            Brackets(b)
        except ValueError:
            invalid.append(str(b)) # Add as string so we can join all invalid to a string
        else:
            valid.append(b)
    invalid_brackets = ", ".join(invalid)
    are_is = "is" if len(invalid) == 1 else "are"
    s = "s" if len(invalid) == 1 else ""
    click.echo(
        f"The following bracket{s} {are_is} invalid and will be ignored: {invalid_brackets}"
        )
    return valid


def setup_grouping(config: dict) -> dict:
    # Determine lowest and highest Grouping enum value
    _g_values = [g.value for g in Grouping]
    grouping_start = min(_g_values)
    grouping_end = max(_g_values)
    
    # Prompt user to select a default grouping
    grouping = "\n".join(f"{g.value}. {g.name.capitalize()}" for idx, g in enumerate(Grouping))
    click.echo(grouping)
    
    default_grouping = click.prompt(
        f"Select default hero grouping ({grouping_start}-{grouping_end})",
        type=int
        )
    
    while default_grouping not in _g_values:
        default_grouping = click.prompt(
            f"Invalid grouping. Try again ({grouping_start}-{grouping_end})",
            type=int
            )
    
    config["grouping"] = default_grouping

    return config


def setup_config_name(config: dict) -> dict:
    click.echo(
        f"Choose a default hero grid name. (current: {config['config_name']})"
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
    click.echo("Do you want to sort heroes by winrates descending or ascending?")
    click.echo("1. Descending [default]")
    click.echo("2. Ascending")
    
    choice = 0
    while choice not in [1, 2]:
        choice = click.prompt("Choice (1-2)", type=int)
    config["sort"] = (choice == 1)

    return config


def run_first_time_setup() -> dict:
    # Create new config file
    if Path("config.yml").exists():
        if not click.confirm(
            "'config.yml' already exists. Are you sure you want to overwrite it?"
            ):
            click.echo("Aborting setup.")
            return
    
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
