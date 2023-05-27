def read_file(path: str) -> str:
    """Reads and returns the content of a file."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def write_file(path: str, contents: str) -> None:
    """Writes the contents to a file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)
