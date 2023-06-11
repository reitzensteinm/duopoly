import os


def read_file(path: str) -> str:
    """Reads and returns the content of a file."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def add_line_numbers(file_contents: str) -> str:
    """Returns the file contents with line numbers added."""
    lines = file_contents.split("\n")
    numbered_lines = [f"{idx+1}: {line}" for idx, line in enumerate(lines)]
    return "\n".join(numbered_lines)


def partition_by_predicate(sequence: list, predicate: callable) -> list:
    """Takes a list(sequence) and a predicate(function that evaluates to a boolean),
    returns a list of lists. The function loops over the input sequence, adding each
    element to a list. Each time the predicate returns true, it starts on a new list
    with that element.

    Args:
        sequence (list): A list of items to be partitioned.
        predicate (callable): A function that returns a boolean.

    Returns:
        list: A list of lists containing partitioned items based on the predicate.
    """
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)
