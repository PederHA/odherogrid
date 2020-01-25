def make_pypi_readme() -> None:
    long_description = ""
    with open("README.md", "r") as f:
        long_description += f.read()
    with open("CHANGELOG.md", "r") as f:
        long_description += f.read()
    with open("PYPIREADME.md", "w") as f:
        f.write(long_description)


if __name__ == "__main__":
    make_pypi_readme()