import copy
import settings
from rope.base.project import Project
from rope.refactor.move import create_move


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
    """Converts a file path to a Python namespace.

    file_path: The file path to convert.
    returns: The namespace as a string.
    """
    if file_path.startswith(settings.CODE_PATH + "/") and file_path.endswith(".py"):
        file_path = file_path[len(settings.CODE_PATH) + 1 : -3]
    return file_path.replace("/", ".")


def fix_imports(file_string: str, old_namespace: str, new_namespace: str) -> str:
    """Replaces the old namespace with the new namespace in import statements.

    file_string: The content of the file as a string.
    old_namespace: The old namespace.
    new_namespace: The new namespace.
    returns: The modified file content.
    """
    lines = file_string.split("\n")
    for i, line in enumerate(lines):
        if "import" in line:
            lines[i] = line.replace(old_namespace, new_namespace)
    return "\n".join(lines)


def move_file_using_rope(
    project_directory: str, relative_from_path: str, relative_to_path: str
) -> None:
    """Moves a file from one path to another using the rope library's Rename tool, treating files as resources.

    project_directory: The path to the root of the project directory.
    relative_from_path: The relative path from the project root to the file to be moved.
    relative_to_path: The relative path from the project root to where the file should be moved.
    """
    rope_project = Project(project_directory)
    try:
        move = create_move(rope_project, rope_project.get_file(relative_from_path))
        move.move(rope_project.get_folder(relative_to_path))
    finally:
        rope_project.close()
