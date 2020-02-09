from collections import defaultdict
from enum import EnumMeta

import click

from .. import __version__
from .params import PARAMS

INDENT_SPACES = 2


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


def print_version(ctx, param, value) -> None:
    click.echo(f"Version {__version__}")
    ctx.exit()


def print_help(ctx, param, value) -> None:
    click.echo(get_help_string())
    ctx.exit()
