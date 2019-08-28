# ODHeroGrid
---
Creates a custom Dota 2 Hero Grid config that sorts heroes by winrate in either public or professional games.

### Usage
```bash
python3.7 odhg.py [--bracket] <1-7 (herald-divine/immortal) OR pro>
                  [--path] <absolute path of Dota 2 userdata cfg directory>
```
ODHeroGrid features OS-agnostic auto detection of the Dota 2 userdata directory if
Steam User ID is configured in `config.py`.