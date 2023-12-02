import copy
import settings
from typing import Any
from rope.base.project import Project
from rope.refactor.move import MoveResource


def move_file(file_mapping, old_path, new_path):
    # Creating a copy of the dictionary
    file_mapping_copy = copy.deepcopy(file_mapping)

    if old_path in file_mapping_copy:
        # Moving the file to the new path
        file_mapping_copy[new_path] = file_mapping_copy.pop(old_path)

        # Generate old_namespace and new_namespace
        old_namespace = path_to_namespace(old_path)
        new_namespace = path_to_namespace(new_path)

        # Iterating over each file and fix broken import paths if any
        for file_path, file_content in file_mapping_copy.items():
            file_mapping_copy[file_path] = fix_imports(
                file_content, old_namespace, new_namespace
            )
    else:
        raise Exception(f"No such file: '{old_path}'")

    return file_mapping_copy


def path_to_namespace(file_path):
    if file_path.startswith(settings.CODE_PATH + "/") and file_path.endswith(".py"):
        file_path = file_path[len(settings.CODE_PATH) + 1 : -3]
    return file_path.replace("/", ".")


def fix_imports(file_string, old_namespace, new_namespace):
    lines = file_string.split("\n")
    for i, line in enumerate(lines):
        if "import" in line:
            lines[i] = line.replace(old_namespace, new_namespace)
    return "\n".join(lines)


def move_file_using_rope(directory: str, from_path: str, to_path: str) -> Any:
    """Move a file from 'from_path' to 'to_path' within a project at 'directory' using the rope library.

    This function accepts a project directory as well as relative from and to paths, and uses the rope library's move_resource function to perform the file move operation.

    Arguments:
    directory: A string representing the path to the project directory.
    from_path: A string representing the relative path from the project directory to the source file.
    to_path: A string representing the relative path from the project directory to the destination.

    Returns:
    Any: Returns an outcome object or raises an exception.
    """
    project = Project(directory)
    resource = project.get_file(from_path)
    mover = MoveResource(project, resource, to_path)
    changes = mover.get_changes()
    project.do(changes)
