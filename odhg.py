import click

from cfg import make_herogrid, get_cfg_path
from config import load_config, run_first_time_setup
from odapi import fetch_hero_stats
from parseargs import parse_arg_brackets, parse_arg_grouping


def get_config_from_cli_arguments(**kwargs) -> dict:
    """Loads config from 'config.yml' and overrides entries 
    corresponding to any CLI arguments. 
    
    Returns config
    """
    # Load config.yml if not all CLI arguments are passed in
    if all(v for v in kwargs.values()):
        config = {}
    else:
        config = load_config()
    
    # Fill config with CLI arguments
    for option, value in kwargs.items():
        if value is not None:
            config[option] = value
    
    # Parse config values
    config = parse_config(config)
    
    return config


def parse_config(config: dict) -> dict:
    config["brackets"] = parse_arg_brackets(config["brackets"])
    config["grouping"] = parse_arg_grouping(config["grouping"])
    
    # We can fall back on preset bracket and grouping defaults
    # But we can't fall back on a preset default Steam userdata directory path
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
@click.option("--brackets", "-b", default=None, multiple=True)
@click.option("--grouping", "-g", default=None)
@click.option("--path", "-p", default=None)
@click.option("--sort", "-s", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--setup", "-S", is_flag=True)
def main(**kwargs) -> None:
    if kwargs.pop("setup", None):
        config = run_first_time_setup()
        kwargs = config
    
    config = get_config_from_cli_arguments(**kwargs)

    # Fetch hero W/L stats from API
    data = fetch_hero_stats()
    
    # Create grid for each specified bracket
    for bracket in config["brackets"]:
        make_herogrid(data, config, bracket)
    

# TODO: Config class?

if __name__ == "__main__":   
    main()
