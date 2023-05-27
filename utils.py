def read_file(path: str) -> str:
    """Reads and returns the content of a file."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def partition_by_predicate(sequence: list, predicate: callable) -> list:
    """Splits the given sequence into groups based on the predicate."""
    result = []
    current_group = []

    for item in sequence:
        if predicate(item):
            if current_group:
                result.append(current_group)
                current_group = []
            current_group.append(item)
        else:
            current_group.append(item)

    if current_group:
        result.append(current_group)

    return result


def write_file(path: str, contents: str) -> None:
    """Writes the contents to a file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)
