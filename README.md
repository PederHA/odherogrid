# ODHeroGrid
![logo](logo.png)

Small script that generates a custom Dota 2 Hero Grid layout of heroes sorted by winrate in public or professional games, using stats from OpenDota.

ODHeroGrid features OS-agnostic auto-detection of the Dota 2 userdata CFG directory if
Steam User ID is configured in `config.py`. The auto-detected path can be overriden at any time using the `--path` argument.

### Usage
```bash
python3.7 odhg.py [-b, --bracket] <1-8> (Herald-Pro) (default: 7)
                  [-p, --path] <absolute path of Dota 2 userdata cfg directory> (default: auto-detect)
                  [-s, --sort] <asc/desc> (default: desc)
```

### Examples
Use program defaults. (Auto-detect CFG directory and use Divine bracket hero stats)
```bash
python3.7 odhg.py
```

Create grid from Herald hero winrates
```bash
python3.7 odhg.py --bracket 1
```

Create grid from Pro hero winrates
```bash
python3.7 odhg.py --bracket 8
```

Create grids from Herald, Divine & Pro hero winrates
```bash
python3.7 odhg.py --bracket 178
```

Create grids from hero winrates in all brackets.
```bash
python3.7 odhg.py --bracket 9
```

Specify a specific Steam user CFG directory
```bash
python3.7 odhg.py --path C:\Program Files (x86)\Steam\userdata\420666\570\remote\cfg
```

![Divine Winrates](screenshot_divine.png)
_Divine winrate hero grid generated on 28/08/2019_