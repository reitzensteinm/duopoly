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


def test_partition_by_predicate():
    test_data = ["A", "B", 1, 2, "C", 3, "D", 4]
    expected_result = [["A", "B"], [1, 2], ["C"], [3], ["D"], [4]]

    result = partition_by_predicate(test_data, lambda x: isinstance(x, int))

    assert result == expected_result, f"Expected {expected_result}, but got {result}"


def write_file(path: str, contents: str) -> None:
    """Writes the contents to a file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)
