import copy
import settings
from rope.base.project import Project
from rope.base import libutils
from typing import Dict


def move_file(
    file_mapping: Dict[str, str], old_path: str, new_path: str
) -> Dict[str, str]:
    """Alters a file_mapping dictionary to reflect moving a file from old_path to new_path, updating namespaces as necessary.
    The 'file_mapping' argument is a dictionary mapping paths to file contents; 'old_path' and 'new_path' are the original and new file paths, respectively.
    Returns an updated dictionary reflecting the moved file."""
    file_mapping_copy = copy.deepcopy(file_mapping)

    if old_path in file_mapping_copy:
        file_mapping_copy[new_path] = file_mapping_copy.pop(old_path)

        old_namespace = path_to_namespace(old_path)
        new_namespace = path_to_namespace(new_path)

        for file_path, file_content in file_mapping_copy.items():
            file_mapping_copy[file_path] = fix_imports(
                file_content, old_namespace, new_namespace
            )
    else:
        raise Exception(f"No such file: '{old_path}'")

    return file_mapping_copy


def move_file_using_rope(project_directory: str, from_path: str, to_path: str) -> None:
    """Moves a file within a project from a source path to a destination path using the rope library.
    The 'project_directory' is the root directory of the project; 'from_path' and 'to_path' are the relative paths of the source file and the target location, respectively.
    This function does not return any value."""
    project = Project(project_directory)
    from_resource = libutils.path_to_resource(project, from_path)
    to_resource = libutils.path_to_resource(project, to_path)

    libutils.move_resource(from_resource, to_resource)


def path_to_namespace(file_path: str) -> str:
    """Converts a file path to a Python namespace by stripping the leading code path and replacing slashes with periods.
    The 'file_path' argument is the original path to be converted to namespace format.
    Returns the converted namespace as a string."""
    if file_path.startswith(settings.CODE_PATH + "/") and file_path.endswith(".py"):
        file_path = file_path[len(settings.CODE_PATH) + 1 : -3]
    return file_path.replace("/", ".")


def fix_imports(file_string: str, old_namespace: str, new_namespace: str) -> str:
    """Updates the import paths inside a file's content from an old namespace to a new namespace.
    The 'file_string' is the content of the file; 'old_namespace' and 'new_namespace' are the original and new namespaces, respectively.
    Returns the updated file content as a string."""
    lines = file_string.split("\n")
    for i, line in enumerate(lines):
        if "import" in line:
            lines[i] = line.replace(old_namespace, new_namespace)
    return "\n".join(lines)
