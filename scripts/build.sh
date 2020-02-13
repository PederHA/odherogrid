SCRIPTPWD=$(dirname "$0")
poetry shell
python $SCRIPTPWD/generate_readme.py
python $SCRIPTPWD/generate_pypi_readme.py
poetry build