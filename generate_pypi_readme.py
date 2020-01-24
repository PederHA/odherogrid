if __name__ == "__main__":
    long_description = ""
    with open("README.md", "r") as f:
        long_description += f.read()
    with open("CHANGELOG.md", "r") as f:
        long_description += f.read()
    with open("PYPIREADME.md", "w") as f:
        f.write(long_description)