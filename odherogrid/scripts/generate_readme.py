from pathlib import Path
from typing import TextIO
from .help import get_cli_help_string
from datetime import datetime


def codeblock(text: str, lang: str="") -> None:
    block = f"""```{lang}
{text}
```"""
    return block


def intro(f: TextIO) -> None:
    text = """# ODHeroGrid
![logo](logo.png)

Small script that generates a custom Dota 2 Hero Grid layout of heroes sorted 
by winrate in public or professional games, using stats from OpenDota.

"""
    f.write(text)



def installation(f: TextIO) -> None:
    text = f"""# Installation
{codeblock('pip install odherogrid')}

"""
    f.write(text)


def usage(f: TextIO) -> None:
    text = f"""# Usage
{codeblock(get_cli_help_string())}

    """
    f.write(text)

def examples(f: TextIO) -> None:
    text = """#
## Bracket


#### Create grid for Herald hero winrates:
```bash
odhg --brackets 1
```

#### Bracket names can also be used:
```bash
odhg --brackets herald
```

#### Shorter:
```bash
odhg -b 1
odhg -b h
```

#
#### Create grids for Herald, Divine & Pro winrates:
```bash
odhg -b 1 -b 7 -b 8
```
#### Alternatively:
```bash
odhg -b h -b d -b p
```
#
#### Create grids for all brackets:
```bash
odhg -b 0
```


#
## Grouping


#### Create grids for Divine hero winrates, grouped by Hero roles (Carry/Support/Flex):
```bash
odhg -g 3 -b 7
```

#### Name of grouping method can also be used:
```bash
odhg -g role -b 7
```


#
## Path


#### Specify a specific Steam user CFG directory:
```bash
odhg --path C:\\Program Files (x86)\\Steam\\userdata\\420666\\570\\remote\\cfg
```


"""
    f.write(text)


def screenshots(f: TextIO) -> None:
    img = Path(__file__).parent.parent.parent / "screenshot_divine.png"
    timestamp = datetime.fromtimestamp(img.stat().st_mtime).isoformat().split("T")[0]

    text = f"""# Screenshots

![Divine Winrates](screenshot_divine.png)
_Divine winrate hero grid generated {timestamp}_
"""
    f.write(text)

if __name__ == "__main__":
    with open(Path(__file__).parent.parent.parent / "README2.md", "w") as f:
        intro(f)
        installation(f)
        usage(f)
        examples(f)
        screenshots(f)