from commands.command import Command
from commands.state import State
from utils import annotate_with_line_numbers


class Files(Command):
    """
    Class representing a Files command.
    """

    @classmethod
    def name(cls) -> str:
        return "Files"

    @property
    def terminal(self):
        return False

    def __init__(self, files: list):
        self.files: list = files

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Files command.
        """
        return {
            "name": "Files",
            "description": "List files and their contents from the state",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "description": "List of files to retrieve",
                        "items": {"type": "string"},
                    }
                },
                "required": ["files"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Files":
        """
        Loads the Files command from the provided json_data.
        """
        return Files(json_data["files"])

    def execute(self, state: State) -> str:
        """
        Executes the Files command.
        """
        result = ""
        for file in self.files:
            if file in state.files:
                annotated_content = annotate_with_line_numbers(state.files[file])
                result += f"{file}: \n{annotated_content}"
        return result
