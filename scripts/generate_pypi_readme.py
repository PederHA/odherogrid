from resources import ODHG_ROOT
from generate_readme import get_readme_string

def make_pypi_readme() -> None:
    long_description = ""
    with open(ODHG_ROOT/"README.md", "r") as f:
        long_description += get_readme_string(noimg=True)
    with open(ODHG_ROOT/"CHANGELOG.md", "r") as f:
        long_description += f.read()
    with open(ODHG_ROOT/"PYPIREADME.md", "w") as f:
        f.write(long_description)


if __name__ == "__main__":
    make_pypi_readme()
    # TODO: Remove all image tags