from typing import List


class Project:
    def __init__(self, path: str):
        """Initialize the Project with a path and an empty list of code paths.

        Args:
                path: A string representing the path to the project.
        """
        self.path = path
        self.code_paths: List[str] = []
