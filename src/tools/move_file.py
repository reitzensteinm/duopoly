import copy
import settings
from rope.base.project import Project
from rope.refactor.move import Move


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


def move_file_using_rope(project_dir: str, from_path: str, to_path: str) -> None:
    """
    Moves a Python file from one path to another within a project using the rope library for refactoring.
    The function takes a project directory as well as the relative from and to paths of the file to be moved.
    It performs refactoring that includes the update of import statements.
    :param project_dir: The path to the base directory of the project.
    :param from_path: The relative path (from the project directory) of the file to move.
    :param to_path: The relative path (to the project directory) where the file should be moved to.
    :return: Nothing, as the file move is a refactoring operation with no value returned.
    """
    # Create a rope project
    rope_project = Project(project_dir)
    # Perform the file move operation
    move = Move(rope_project, from_path, to_path)
    move.perform()
    # Release resources used by rope project
    rope_project.close()
