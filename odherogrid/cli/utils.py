from contextlib import contextmanager

import click


@contextmanager
def progress(message: str, 
             success: str="✔️", 
             width: int=25, 
             ljust: bool=True, 
             nl: bool=False
            ) -> None:
    message = message.ljust(width) if ljust else message.rjust(width)
    click.echo(message, nl=False)
    try:
        yield
    finally:
        click.echo(success)
