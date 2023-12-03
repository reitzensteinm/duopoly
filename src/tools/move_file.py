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


def path_to_namespace(file_path: str) -> str:
    """Convert a file path to a Python namespace by removing the common prefix and '.py' extension, and replacing slashes with dots. Args: file_path: The file path as a string. Returns: The converted file namespace as a string."""
    if file_path.startswith(settings.CODE_PATH + "/") and file_path.endswith(".py"):
        file_path = file_path[len(settings.CODE_PATH) + 1 : -3]
    return file_path.replace("/", ".")


def fix_imports(file_string: str, old_namespace: str, new_namespace: str) -> str:
    """Fix the import statements in the file content after the file has been moved by replacing the old namespace with the new namespace. Args: file_string: The file content as a string. old_namespace: The old namespace to be replaced. new_namespace: The new namespace to use. Returns: The updated file content with fixed import statements."""
    lines = file_string.split("\n")
    for i, line in enumerate(lines):
        if "import" in line:
            lines[i] = line.replace(old_namespace, new_namespace)
    return "\n".join(lines)


def move_file_using_rope(project_directory: str, from_path: str, to_path: str) -> None:
    """Move a file within a project directory from one path to another by using the rope library's Rename tool. Args: project_directory: The root directory of the project as a string. from_path: The original file path relative to the project directory. to_path: The new file path relative to the project directory."""
    project = Project(project_directory)
    resource = project.get_file(from_path)
    new_name = to_path.split("/")[-1]  # Extracting the new file name
    Rename(project, resource).get_changes(new_name).perform()
