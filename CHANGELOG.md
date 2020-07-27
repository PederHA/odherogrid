# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## 0.3.0 (July xxth, 2020)
### Added
- Immortal bracket support (`-b [8, "i", "immortal"]`)

### Changed
- Parameter `--sort` renamed to `--ascending`



## 0.2.0 (February 14th, 2020)
### Added
- Attempt to adhere to [Semantic Versioning](http://semver.org/)
- `--quiet` option to suppress stdout. Errors are still displayed.
- Printing of program progress ("Fetching data", "generating grids", etc.).
- Printing of ASCII table displaying generated grids upon program completion.

### Changed
- Parameter `--grouping` renamed to `--layout`.
- Layout `none` renamed to `single`.
- Large parts of the program have been rewritten, but user experience should be identical.
- Logo has received a small facelift.

## 0.1.2 (January 24th, 2020)
### Added
- Sorting of specific custom grids by using the `--name` parameter

### Changed
- ~/.odhg/config.yml now lists full path of hero_grid_config.json instead of just its directory.