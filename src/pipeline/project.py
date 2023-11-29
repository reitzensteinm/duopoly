from typing import List
import yaml


class Project:
    def __init__(self, path: str):
        """Initialize the Project with a path and an empty list of code paths.

        Args:
                path: A string representing the path to the project.
        """
        self.path = path
        self.code_paths: List[str] = []

    def load_from_yaml(self, filepath: str = "duopoly.yaml") -> None:
        """Load project-specific settings like code paths from a 'project' subsection of a YAML file.

        Args:
                filepath (str): The path to the YAML file that contains the project settings.

        This method updates the instance with settings from the 'project' subsection of the YAML file at `filepath`.
        """
        with open(filepath, "r") as yamlfile:
            data = yaml.safe_load(yamlfile)
        if "project" in data:
            project_data = data["project"]
            if "code_paths" in project_data:
                self.code_paths = project_data["code_paths"]
