# ODHeroGrid
![logo](logo.png)
Small script that generates a custom Dota 2 Hero Grid layout of heroes sorted by winrate in public or professional games, using stats from OpenDota.

ODHeroGrid features OS-agnostic auto-detection of the Dota 2 userdata CFG directory if
Steam User ID is configured in `config.py`, but the auto detected path can be overriden at any time by using the `--path` argument.

### Usage
```bash
python3.7 odhg.py [--bracket] <1-7 (herald-divine/immortal) OR pro> (default: 7)
                  [--path] <absolute path of Dota 2 userdata cfg directory> (default: auto detect)
```

### Examples
Use program defaults. (Auto-detect CFG directory and use divine bracket hero stats)
```bash
python3.7 odhg.py
```

Use herald bracket hero stats
```bash
python3.7 odhg.py --bracket 1
```

Use hero stats from official pro games only
```bash
python3.7 odhg.py --bracket pro
```

Specify a specific Steam user CFG directory
```bash
python3.7 odhg.py --path C:\Program Files (x86)\Steam\userdata\420666\570\remote\cfg
```

![Divine Winrates](screenshot_divine.png)
_Divine winrate hero grid generated on 28/08/2019_