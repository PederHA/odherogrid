from pathlib import Path

import click

from .cfg import make_herogrid, get_cfg_path
from .config import load_config, run_first_time_setup
from .odapi import fetch_hero_stats
from .parseargs import parse_arg_brackets, parse_arg_grouping


def get_help_string() -> dict:
    """Gets help string from README.md"""
    p = Path(__file__)
    with open(p.parent.parent / "README.md", "r") as f:
        readme = f.read()
    lines = []
    active = False
    start_md = False
    for line in readme.splitlines():
        if line.startswith("# Usage"):
            active = True
            continue
        if active:
            if line.startswith("```"):
                if not start_md:
                    start_md = True
                    continue
                else:
                    break # break out once we have reached end of codeblock
            else:
                lines.append(line)
    return "\n".join(lines)



def get_config_from_cli_arguments(**options) -> dict:
    """Fills missing arguments using values from 'config.yml'.
    
    Returns config
    """
    # Load config.yml if not all CLI arguments are passed in
    if all(v for v in options.values()):
        config = options
    else:
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
@click.option("--brackets", "-b", default=None, multiple=True)
@click.option("--grouping", "-g", default=None)
@click.option("--path", "-p", default=None) # we forego click.Path here and do our own check
@click.option("--sort", "-s", is_flag=True, default=True) # enable for ascending sorting # TODO: rename sort to one of [sort, sortasc, asc, ascending]
@click.option("--setup", "-S", is_flag=True)
@click.option("--help", is_flag=True)
def main(**options) -> None:
    if options.pop("help"):
        click.echo("USAGE:")
        click.echo(get_help_string())
        raise SystemExit
    
    if options.pop("setup", None):
        options = run_first_time_setup()
        # Ask if user wants to generate grid?
    
    config = get_config_from_cli_arguments(**options)

    # Fetch hero W/L stats from API
    data = fetch_hero_stats()
    
    # Create grid for each specified bracket
    for bracket in config["brackets"]:
        make_herogrid(data, config, bracket)
    

# TODO: Config class?

if __name__ == "__main__":   
    main()
