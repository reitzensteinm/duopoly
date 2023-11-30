from typing import List
import yaml
import os


class Project:
    def __init__(self, path: str):
        """Initialize the Project with a path, an empty list of code paths, and load settings from 'duopoly.yaml' if it exists.

        Args:
                path: A string representing the path to the project.

        During initialization, if a 'duopoly.yaml' file exists in the project path, it attempts to load settings from it.
        """
        self.path = path
        self.code_paths: List[str] = []
        duopoly_yaml_path = os.path.join(self.path, "duopoly.yaml")
        if os.path.exists(duopoly_yaml_path):
            self.load_from_yaml(duopoly_yaml_path)

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
