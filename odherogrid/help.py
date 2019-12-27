from collections import namedtuple, defaultdict
from enum import Enum, EnumMeta
from typing import NamedTuple, Iterable, Any, Optional

from .parseargs import GROUPING, BRACKETS
from .enums import Brackets, Grouping

INDENT_SPACES = 2

class Param(NamedTuple):
    """Describes an ODHG CLI parameter."""
    # TODO: option_short, option_long ?
    options: Iterable[str]
    argument_format: str
    description: str
    arguments: dict = None
    argument_type: Optional[Enum] = None # this is quite hacky
    description_post: str = None


# TODO: params dict with "help", "setup" etc. keys
#       dynamically add click.parameter decorators to odhg.main
params = [
    Param(
        options=["-b", "--brackets"],
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
        argument_format="(flag)",
        description="Sort heroes by winrate in ascending order. (Default: descending).",
    ),
    Param(
        options=["-S", "--setup"],
        argument_format="(flag)",
        description= "Runs first-time setup in order to create a persistent config.",
    ),
    Param(
        options=["-n", "--name"],
        argument_format="NAME",
        description="""Sort heroes by winrate in an already existing custom hero grid.""",
    ),
    Param(
        options=["-h", "--help"],
        argument_format="(flag)",
        description= "Show this message and exit.",
    ),
]

def indent(steps: int) -> str:
    return " "*INDENT_SPACES * steps

def get_cli_help_string() -> str:
    ident = lambda i: " "*i
    BASE_INDENT = 1

    lines = []
    lines.append("Usage:")
    lines.append(f"{indent(BASE_INDENT)}odhg [OPTIONS]")
    lines.append("\nOptions:")
    for p in params:
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
