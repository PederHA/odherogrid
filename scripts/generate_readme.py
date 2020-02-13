from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Callable

from odherogrid.cli import get_help_string

from resources import ODHG_ROOT



def imagefunc(f) -> Callable[..., str]:
    f.has_img = True
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def codeblock(text: str, lang: str="") -> str:
    block = f"""```{lang}
{text}
```"""
    return block

@imagefunc
def intro(img: bool=True) -> str:
    text = f"""# ODHeroGrid
{'![logo](logo.png)' if img else ''}

Small script that generates a custom Dota 2 Hero Grid layout of heroes sorted 
by winrate in public or professional games, using stats from OpenDota.

"""
    return text


def installation() -> str:
    text = f"""# Installation
{codeblock('pip install odherogrid')}

"""
    return text


def usage() -> str:
    text = f"""# Usage
{codeblock(get_help_string())}
## Using standard configuration 
{codeblock("odhg")}
Prompts to create config file in `~/.odhg/` the first time the program runs.

This is the recommended way to run ODHG.
"""
    return text

def examples() -> str:
    text = f"""# Command-line options
Command-line options can be supplied to override config settings.


## Bracket


#### Create grid for Herald hero winrates:
{codeblock("odhg --brackets 1")}


#### Bracket names can also be used:
{codeblock("odhg --brackets herald")}


#### Shorter:
{codeblock("odhg -b h")}


#
#### Create grids for Herald, Divine & Pro winrates:
{codeblock("odhg -b 1 -b 7 -b 8")}

#### Alternatively:
{codeblock("odhg -b h -b d -b p")}


#
#### Create grids for all brackets:
{codeblock("odhg -b 0")}


## Layout
#### Use role layout (Carry/Support/Flex). 
{codeblock("odhg --layout role")}

#### Single category layout
{codeblock("odhg --layout single")}


## Path
#### Specify a specific Steam user CFG directory:
{codeblock("odhg --path /home/bob/Steam/userdata/420666/570/remote/cfg")}

"""
    return text


@imagefunc
def name(img: bool=True) -> str:
    if not img:
        return ""

    pre = "screenshots/custom_presort.png"
    post = "screenshots/custom_postsort.png"

    text = f"""## Name
#### Sort custom grids with `--name`
{codeblock("odhg --name MyCustomGrid -b 7")}
#### Before:
![Before]({pre})
#### After:
![After]({post})
"""
    return text


@imagefunc
def screenshots(img: bool=True) -> str:
    if not img:
        return ""

    fname = "screenshots/screenshot.png"

    img = Path(fname)
    timestamp = datetime.fromtimestamp(img.stat().st_mtime).isoformat().split("T")[0]

    text = f"""# Screenshots

![Divine Winrates]({fname})
_Divine winrate hero grid generated {timestamp}_
"""
    return text


def get_readme_string(noimg: bool=False) -> str:
    s = []
    for f in sections:
        if noimg and hasattr(f, "has_img"):
            r = f(img=False)
        else:
            r = f()
        s.append(r)
    return "\n".join(s)


sections = [intro, installation, usage, examples, name, screenshots]


def makereadme() -> None:
    with open(ODHG_ROOT/"README.md", "w") as f:
        f.write(get_readme_string())


if __name__ == "__main__":
    makereadme()

