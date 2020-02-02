from collections import namedtuple, defaultdict
from enum import Enum, EnumMeta
from typing import NamedTuple, Iterable, Any, Optional, Type, List

import click

from . import __version__
from .parseargs import GROUPING, BRACKETS
from .enums import Brackets, Grouping


INDENT_SPACES = 2


# since we can't subclass click.Parameter, we have to do this
class Param(NamedTuple):
    """Describes an ODHG CLI parameter."""
    # TODO: option_short, option_long ?

    # click.Parameter
    options: Iterable[str]
    default: Any = None
    is_flag: bool = False
    type: Type = None
    multiple: bool = False
    callback: Any = None

    # state
    enabled: bool = True
    
    # Help text
    argument_format: str = ""
    description: str = ""
    arguments: dict = None
    argument_type: Optional[Enum] = None # this is quite hacky
    description_post: str = None


def indent(steps: int) -> str:
    return " "*INDENT_SPACES * steps


def get_help_string() -> str:
    BASE_INDENT = 1 # steps

    lines = []
    lines.append("Usage:")
    lines.append(f"{indent(BASE_INDENT)}odhg [OPTIONS]")
    lines.append("\nOptions:")
    for p in PARAMS:
        if not p.enabled:
            continue
        # Add option(s) and argument format. E.g. "[-o, --option] OPTION"
        lines.append(f"{indent(BASE_INDENT)}[{', '.join(p.options)}] {p.argument_format}")

        # Add description
        lines.append(indent(BASE_INDENT+1) + p.description)

        # Add valid arguments (if any)
        if p.arguments:
            args = defaultdict(list)
            for arg, value in p.arguments.items():
                args[value].append(arg)
            for i, vals in args.items():
                a = f"<{', '.join(str(v) for v in vals)}>"
                # Get name associated with Enum value if arg type is Enum
                if type(p.argument_type) == EnumMeta:
                    argval = p.argument_type(i).name.capitalize()
                else:
                    argval = ""
                lines.append(indent(BASE_INDENT+2) + a + " "*(40-len(a)) + argval)
        
        if p.description_post:
            lines.append(indent(BASE_INDENT+1) + p.description_post)
        
        lines.append("")
    return "\n".join(lines)


def get_click_params() -> List[click.Option]:  
    return [
        click.Option(
            p.options,
            default=p.default,
            is_flag=p.is_flag,
            type=p.type,
            multiple=p.multiple,
            callback=p.callback
        )
        for p in PARAMS
        if p.enabled
    ]


def print_version(ctx, param, value) -> None:
    click.echo(f"Version {__version__}")
    ctx.exit()


def print_help(ctx, param, value) -> None:
    click.echo(get_help_string())
    ctx.exit()


# This is the alternative to stacking decorators on odhg.main()
# and it also makes it easier to gather documentation and behavior 
# of command parameters in one place
PARAMS = [
    Param(
        options=["-b", "--brackets"],
        multiple=True,
        argument_format=f"BRACKET (default: {Brackets.DEFAULT})",
        description="Which skill bracket to get winrates from.", 
        arguments=BRACKETS,
        argument_type=Brackets,
        description_post="Hero grids for multiple brackets can be generated "
                         "by specifying the -b option several times."
    ),
    Param(
        options=["-g", "--grouping"],
        argument_format=f"GROUPING (default: {Grouping.DEFAULT})",
        description="How heroes should be grouped in the grid",
        arguments=GROUPING,
        argument_type=Grouping
    ),
    Param(
        options=["-p", "--path"],
        argument_format="PATH",
        description="Specify absolute path of Dota 2 userdata/cfg directory.",
        description_post="(It's usually better to run --setup to configure this path.)",
    ),
    Param(
        options=["-s", "--sort"],
        is_flag=True,
        default=True,
        argument_format="(flag)",
        description="Sort heroes by winrate in ascending order. (Default: descending).",
    ),
    Param(
        options=["-S", "--setup"],
        is_flag=True,
        argument_format="(flag)",
        description= "Runs first-time setup in order to create a persistent config.",
    ),
    Param(
        options=["-n", "--name"],
        type=str,
        argument_format="NAME",
        description="""Sort heroes by winrate in an already existing custom hero grid.""",
    ),
    Param(
        options=["--version"],
        is_flag=True,
        argument_format="(flag)",
        description= "Show program version.",
        enabled=False
    ),
    Param(
        options=["-h", "--help"],
        is_flag=True,
        argument_format="(flag)",
        description= "Show this message and exit.",
    ),
    Param(
        options=["--schedule"],
        is_flag=True,
        argument_format="(flag)",
        description= "Schedule ODHG to run periodically.\n"
                     "(crontab on UNIX-like systems, Task Scheduler on Windows)",
        enabled=False

    ),
]