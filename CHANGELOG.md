# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## 0.2.0 (February XXth, 2020)
### Added
- Attempt to adhere to [Semantic Versioning](http://semver.org/)
- `--quiet` option to suppress stdout. Errors are still displayed.
- Printing of program steps ("Fetching data", "generating grids", etc.)
- Printing of ASCII table displaying generated grids upon program completion.

### Changed
- Handling of multiple bracket arguments is now performed by `cfg.make_new_hero_grid()` (was `odhg.main()`).

## 0.1.2 (January 24th, 2020)
### Added
- Sorting of specific custom grids by using the `--name` parameter

### Changed
- ~/.odhg/config.yml now lists full path of hero_grid_config.json instead of just its directory.