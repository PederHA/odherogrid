from collections import namedtuple, defaultdict
from enum import Enum, EnumMeta
from typing import NamedTuple, Iterable, Any, Optional

from .parseargs import GROUPING, BRACKETS
from .enums import Brackets, Grouping


class Param(NamedTuple):
    options: Iterable[str]
    argument_format: str
    description: str
    arguments: dict = None
    argument_type: Optional[Enum] = None # this is quite hacky
    description_post: str = None


params = [
    Param(
        options=["-b", "--brackets"],
        argument_format=f"BRACKET (default: {Brackets.DEFAULT})",
        description="Which skill bracket to get winrates from.", 
        arguments=BRACKETS,
        argument_type=Brackets,
        description_post="""Hero grids for multiple brackets can be generated
        by specifying the -b option several times."""
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
        description="""Specify absolute path of Dota 2 userdata/cfg directory.
        (It's usually better to run --setup to configure this path.)""",
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
        options=["-h", "--help"],
        argument_format="(flag)",
        description= "Displays command usage information.",
    ),
]


def get_cli_help_string() -> str:
    ident = lambda i: " "*i
    lines = []
    lines.append("odhg  ")
    i = 0
    for idx, p in enumerate(params):
        if idx != 0:
            lines.append(ident(6))
        
        # Add option(s) and argument format. E.g. "[-o, --option] OPTION"
        lines[len(lines)-1] += f"[{', '.join(p.options)}] {p.argument_format}"

        # Add description
        lines.append(ident(8) + p.description)

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
                lines.append(ident(12) + a + ident(40-len(a)) + argval)
        lines.append("")
    return "\n".join(lines)
