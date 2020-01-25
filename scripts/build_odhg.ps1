poetry shell
python $PSScriptRoot\generate_readme.py
python $PSScriptRoot\generate_pypi_readme.py
poetry build