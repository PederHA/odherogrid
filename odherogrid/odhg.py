from pathlib import Path
from typing import List

import click
from terminaltables import SingleTable

from .cfg import make_new_herogrids, modify_existing_herogrid, get_hero_grid_config_path
from .config import load_config, run_first_time_setup, CONFIG_BASE
from .odapi import fetch_hero_stats
from .parseargs import parse_arg_brackets, parse_arg_grouping
from .cli import get_help_string, get_click_params
from .error import handle_exception


def get_config_from_cli_args(**options) -> dict:
    """Fills missing CLI arguments using values from 'config.yml'.
    
    Returns config
    """
    
    # Use kwargs as config if all required config keys are specified
    # and their values are not None
    if options and all(
        k in options 
        and options.get(k, None) is not None
        for k in CONFIG_BASE.keys()
    ):
        config = options
    else: # Load config.yml if not all required config keys are passed in
          # as CLI arguments.
        config = load_config() # If no config exists, first-time setup is run.
        # Add missing args using values from config.yml
        for option, arg in options.items():
            if arg or arg == 0: # we need to accept 0 as a valid arg
                # TODO: Check if we can just write if arg not in [None, []]
                #       or arg is not None
                config[option] = arg

    # Parse config values
    config = parse_config(config)
    
    return config


def parse_config(config: dict) -> dict:
    config["brackets"] = parse_arg_brackets(config["brackets"])
    config["grouping"] = parse_arg_grouping(config["grouping"])
    
    # We can fall back on bracket and grouping defaults
    # But we can't fall back on a default Steam userdata directory path
    try:
        config["path"] = get_hero_grid_config_path(config["path"]) # Steam userdata directory
    except (TypeError, ValueError) as e:
        click.echo(e.args[0])
        click.echo(
            "Either specify a valid path using the '--path' option, "
            "or run setup using the '--setup' flag to permanently add "
            "a valid path to your config."
        )
        raise SystemExit
    return config


def print_gridnames(config: dict, grids: List[str]) -> None:
    #g = "\n".join([f"\t'{_g}'" for _g in grids]) # add single quotes + tab
    #table = SingleTable([["Grid Name"], grids])
    table = SingleTable([[g] for g in grids])
    click.echo(f"Successfully created the following grids:\n{table.table}\n")
    click.echo(f"Changes were saved to {config['path']}")


@click.command()
def main(**options) -> None:
    if options.pop("help", None):
        click.echo(get_help_string())
        raise SystemExit
    
    if options.pop("setup", None):
        options = run_first_time_setup()

    if options.pop("quiet"):
        def _ignore(*args, **kwargs):
            pass
        click.echo = _ignore

    name = options.pop("name", None) # Sorting of custom grids (--name)

    config = get_config_from_cli_args(**options)

    # Fetch hero W/L stats from API
    click.echo("Fetching hero data... ", nl=False)
    data = fetch_hero_stats()
    click.echo("✓\n")
    
    click.echo("Creating grids... ", nl=False)
    if name: # Sort custom grid
        grids = modify_existing_herogrid(data, config, name)
    else:    # Make new grid
        grids = make_new_herogrids(data, config)
    click.echo("✓\n")

    print_gridnames(config, grids)


# add parameters defined in cli.py	
main.params.extend(get_click_params())


def _main(**kwargs) -> None:
    """Experimental main() alternative with an exception handler."""
    try:
        main(**kwargs)
    except Exception as e:
        handle_exception(e)

if __name__ == "__main__":
    _main()

