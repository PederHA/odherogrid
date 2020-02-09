from pathlib import Path
from typing import List

import click
from terminaltables import SingleTable

from .cli.help import get_help_string
from .cli.params import get_click_params
from .cli.parse import parse_arg_brackets, parse_arg_grouping, parse_config
from .cli.utils import progress
from .config import CONFIG_BASE, load_config, run_first_time_setup
from .error import handle_exception
from .herogrid import HeroGridConfig, get_hero_grid_config_path
from .odapi import fetch_hero_stats


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


def print_gridnames(config: dict, grids: List[str]) -> None:
    #g = "\n".join([f"\t'{_g}'" for _g in grids]) # add single quotes + tab
    #table = SingleTable([["Grid Name"], grids])
    table = SingleTable([[g["config_name"]] for g in grids])
    click.echo(f"Successfully created the following grids:\n{table.table}\n")
    click.echo(f"Changes were saved to {config['path']}")
    

@click.command()
def main(**options) -> None:
    if options.pop("help", None):
        click.echo(get_help_string())
        raise SystemExit
    
    if options.pop("setup", None):
        conf = run_first_time_setup()
        options.update(conf)

    if options.pop("quiet"):
        def _ignore(*args, **kwargs):
            pass
        click.echo = _ignore

    name = options.pop("name", None) # Sorting of custom grids (--name)

    config = get_config_from_cli_args(**options)

    # Fetch hero W/L stats from API
    with progress("Fetching hero data... "):
        hero_stats = fetch_hero_stats()
    
    with progress("Creating grids... "):
        h = HeroGridConfig(hero_stats, config)
        if name: # Sort custom grid
            h.modify_grid(name)
        else:    # Make new grid
            h.create_grids()


    print_gridnames(config, h.grids)


# add parameters defined in cli.py	
main.params.extend(get_click_params())


def _main(**kwargs) -> None:
    """Experimental main() alternative with an exception handler."""
    try:
        main(**kwargs)
    except Exception as e:
        handle_exception(e)

if __name__ == "__main__":
    main()
