from datetime import datetime
from pathlib import Path

from odherogrid.cli import get_help_string

from resources import ODHG_ROOT


def codeblock(text: str, lang: str="") -> str:
    block = f"""```{lang}
{text}
```"""
    return block


def intro() -> str:
    text = """# ODHeroGrid
![logo](logo.png)

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

"""
    return text

def examples() -> str:
    text = f"""# Examples


#### Use options stored in config. (Runs first-time setup if no config exists)
{codeblock("odhg")}
The config file will be stored as `~/.odhg/config.yml`

It is recommended to create a config rather than using command-line options.


#
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


#
## Grouping


#### Create grids for Divine hero winrates, grouped by Hero roles (Carry/Support/Flex):
{codeblock("odhg -g 3 -b 7")}

#### Name of grouping method can also be used:
{codeblock("odhg -g role -b 7")}


#
## Path


#### Specify a specific Steam user CFG directory:
{codeblock("odhg --path /home/bob/Steam/userdata/420666/570/remote/cfg")}

"""
    return text


def screenshots() -> str:
    fname = "screenshot.png"

    img = Path(fname)
    timestamp = datetime.fromtimestamp(img.stat().st_mtime).isoformat().split("T")[0]

    text = f"""# Screenshots

![Divine Winrates]({fname})
_Divine winrate hero grid generated {timestamp}_
"""
    return text

if __name__ == "__main__":
    with open(ODHG_ROOT/"README.md", "w") as f:
        for func in [intro, installation, usage, examples, screenshots]:
            f.write(func())
