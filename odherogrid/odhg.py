from pathlib import Path

import click

from .cfg import make_new_herogrid, modify_existing_herogrid, get_cfg_path
from .config import load_config, run_first_time_setup
from .odapi import fetch_hero_stats
from .parseargs import parse_arg_brackets, parse_arg_grouping
from .cli import get_help_string, get_click_params


def get_config_from_cli_arguments(**options) -> dict:
    """Fills missing arguments using values from 'config.yml'.
    
    Returns config
    """
    
    if all(v for v in options.values()):
        config = options
    else: # Load config.yml if not all CLI arguments are passed in
        config = load_config()
        # Fill config with CLI arguments
        for option, argument in options.items():
            if argument or argument == 0: # we need to accept 0
                config[option] = argument

    # Parse config values
    config = parse_config(config)
    
    return config


def parse_config(config: dict) -> dict:
    config["brackets"] = parse_arg_brackets(config["brackets"])
    config["grouping"] = parse_arg_grouping(config["grouping"])
    
    # We can fall back on bracket and grouping defaults
    # But we can't fall back on a default Steam userdata directory path
    try:
        config["path"] = get_cfg_path(config["path"]) # Steam userdata directory
    except (TypeError, ValueError) as e:
        click.echo(e.args[0])
        click.echo(
            "Either specify a valid path using the '--path' option, "
            "or run setup using the '--setup' flag to permanently add "
            "a valid path to your config."
        )
        raise SystemExit
    return config


@click.command()
def main(**options) -> None:
    if options.pop("schedule", None):
        pass # NYI
    
    if options.pop("help", None):
        click.echo(get_help_string())
        raise SystemExit
    
    if options.pop("setup", None):
        options = run_first_time_setup()
        # Ask if user wants to generate grid?

    name = options.pop("name", None)
    
    config = get_config_from_cli_arguments(**options)
    
    # Fetch hero W/L stats from API
    data = fetch_hero_stats()
    
    # Create grid for each specified bracket
    for bracket in config["brackets"]:    
        if name: # TODO: Only supports 1 bracket
            modify_existing_herogrid(data, config, name, bracket) 
            break
        else:
            make_new_herogrid(data, config, bracket)


if __name__ == "__main__":   
    main()

