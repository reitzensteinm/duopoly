import copy
import settings
from rope.base import project as rope_project
from rope.refactor.rename import Rename


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


def path_to_namespace(file_path: str) -> str:
    """
    Convert a file path to a Python namespace by stripping the code path prefix and replacing slashes with dots.

    Arguments:
    file_path: The file path to convert.
    Returns:
    The converted namespace as a string.
    """
    if file_path.startswith(settings.CODE_PATH + "/") and file_path.endswith(".py"):
        file_path = file_path[len(settings.CODE_PATH) + 1 : -3]
    return file_path.replace("/", ".")


def fix_imports(file_string: str, old_namespace: str, new_namespace: str) -> str:
    """
    Update the import statements in the provided file content from the old namespace to the new namespace.

    Arguments:
    file_string: The content of the file as a string.
    old_namespace: The old namespace to be replaced.
    new_namespace: The new namespace to replace with.
    Returns:
    The updated content of the file as a string.
    """
    lines = file_string.split("\n")
    for i, line in enumerate(lines):
        if "import" in line:
            lines[i] = line.replace(old_namespace, new_namespace)
    return "\n".join(lines)


def move_file_using_rope(
    project_dir: str, from_rel_path: str, to_rel_path: str
) -> None:
    """
    Moves a file from one path to another within a given project directory using the rope library's Rename refactoring tool.

    This function will create a rope project, use the Rename refactoring tool to rename the file and apply the changes to the filesystem.
    Arguments:
    project_dir: The path to the project directory.
    from_rel_path: The current relative path of the file to be moved.
    to_rel_path: The new relative path for the file after moving.
    Returns:
    None
    """
    proj = rope_project.Project(project_dir)
    resource = proj.get_file(from_rel_path)
    renamer = Rename(proj, resource)
    to_file_name = to_rel_path.split("/")[-1]
    changes = renamer.get_changes(to_file_name)
    proj.do(changes)
