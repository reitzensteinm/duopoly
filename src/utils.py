import os
import threading
from black import FileMode, format_str
from typing import Callable, Any
from queue import Queue
from time import sleep
from functools import wraps


class TimeoutException(Exception):
    """Custom exception class to handle timeout situations."""

    pass


def read_file(path: str) -> str:
    """Reads and returns the content of a file."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def add_line_numbers(file_contents: str) -> str:
    """Returns the file contents with line numbers added."""
    lines = file_contents.split("\n")
    numbered_lines = [f"{idx + 1}: {line}" for idx, line in enumerate(lines)]
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
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)


def replace_spaces_with_tabs(content: str) -> str:
    """
    Replaces spaces at the beginning of each line with tabs.

    Args:
            content (str): The string content to process.

    Returns:
            str: The modified string where initial spaces are replaced with tabs.
    """
    return "\n".join(
        line.replace("    ", "\t", 1) if line.startswith("    ") else line
        for line in content.split("\n")
    )


def annotate_with_line_numbers(content: str) -> str:
    """
    Annotate a file content with line numbers.
    Now handles empty content, and returns '1: <blank line>'.
    """
    if not content:
        return "1: <blank line>"
    annotated_lines = [
        f"{i + 1}: {line}" for i, line in enumerate(content.splitlines())
    ]
    return "\n".join(annotated_lines)


def format_python_code(code: str) -> str:
    formatted_code = format_str(code, mode=FileMode())
    return formatted_code


def list_files(files):
    file_info = ""
    for k, v in files.items():
        file_info += f"{k}:\n{add_line_numbers(v)}\n"
    return file_info


def synchronize_files_write(target_dir, old_files, updated_files):
    """Writes the contents of updated_files to disk and removes files that no longer exist."""
    for k, v in updated_files.items():
        write_file(os.path.join(target_dir, k), v)
    deleted_files = [f for f in old_files.keys() if f not in updated_files]
    for f in deleted_files:
        os.remove(os.path.join(target_dir, f))


def synchronize_files_read(target_dir, old_files, updated_files):
    """
    Copies file contents from the disk into updated_files. Removes entries from updated_files if they no longer exist on disk.
    This does not add new files that have been added to the disk.
    """
    for root, dirs, files in os.walk(target_dir):
        for file_name_on_disk in files:
            relative_path = os.path.relpath(
                os.path.join(root, file_name_on_disk), target_dir
            )
            if relative_path in updated_files:
                with open(
                    os.path.join(root, file_name_on_disk), "r", encoding="utf-8"
                ) as file:
                    updated_files[relative_path] = file.read()
    files_not_found = set(old_files.keys()) - set(updated_files.keys())
    for file_name in files_not_found:
        updated_files.pop(file_name, None)


def run_with_timeout(function: Callable, timeout: float) -> Any:
    """
    Executes a callable function on a separate thread with a specified timeout.
    Raises a TimeoutException if the call is not completed within the timeout period; returns the result otherwise.

    Args:
            function (Callable): The function to be executed.
            timeout (float): The time in seconds within which the function should complete.

    Returns:
            Any: The result of the function if it completes in time.

    Raises:
            TimeoutException: If the function does not complete within the given timeout.
    """

    def wrapper(queue: Queue):
        try:
            result = function()
            queue.put(result)
        except Exception as e:
            queue.put(e)

    queue = Queue()
    thread = threading.Thread(target=wrapper, args=(queue,))
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        thread.join()  # Ensure resources are cleaned up
        raise TimeoutException("Function call timed out.")
    else:
        result = queue.get()
        if isinstance(result, Exception):
            raise result
        return result


def timeout(seconds: float) -> Callable:
    """
    Decorator that executes the decorated function with a specified timeout period
    using the run_with_timeout function. If the function execution exceeds the timeout period,
    it raises a TimeoutException.

    Args:
        seconds (float): The number of seconds allocated as the timeout for the function execution.

    Returns:
        Callable: The wrapped function that will be executed with the specified timeout.
    """

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapped(*args, **kwargs) -> Any:
            return run_with_timeout(lambda: function(*args, **kwargs), seconds)

        return wrapped

    return decorator
