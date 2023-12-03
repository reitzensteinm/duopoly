import copy
import settings
from rope.base.project import Project
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


def move_file_using_rope(project_directory: str, from_path: str, to_path: str) -> None:
    """
    Move a file within a project directory from one path to another using rope's Rename tool.

    This function takes a project directory and relative 'from' and 'to' paths, uses the rope library's Rename tool
    to create a changeset for renaming the file on disk, and applies this changeset using project.do(changes).

    Args:
            project_directory: The directory of the project where the file is located.
            from_path: The relative path of the file to move.
            to_path: The relative path to move the file to.

    Returns:
            None
    """
    project = Project(project_directory)
    resource = project.get_file(from_path)
    renamer = Rename(project, resource)
    changes = renamer.get_changes(new_name=to_path)
    project.do(changes)
    project.validate()
    project.commit()
