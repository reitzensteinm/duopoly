from commands.command import Command
from commands.state import State
from utils import format_python_code
from tools.replace_file import modify_file


class ReplaceFile(Command):
    """
    Class representing ReplaceFile command.
    """

    @classmethod
    def name(cls) -> str:
        return "ReplaceFile"

    @property
    def terminal(self):
        return False

    def __init__(self, filename: str, instructions: str):
        self.filename: str = filename
        self.instructions: str = instructions

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the ReplaceFile command.
        """
        return {
            "name": "ReplaceFile",
            "description": "Modify a file with the given instructions. This command returns a special token for the new file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to be replaced",
                    },
                    "instructions": {
                        "type": "string",
                        "description": "Human readable description for how the file should be modified, without code",
                    },
                },
                "required": ["filename", "instructions"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "ReplaceFile":
        """
        Loads the ReplaceFile command from the provided json_data.
        """
        return ReplaceFile(json_data["filename"], json_data["instructions"])

    def execute(self, state: State):
        """
        Executes the ReplaceFile command.
        """
        new_content = modify_file(
            state.files.get(self.filename, ""),
            self.instructions,
            state.scratch,
            self.filename,
        )
        if self.filename.endswith(".py"):  # Check if it's a Python file
            new_content = format_python_code(
                new_content
            )  # Format the content if it's a Python file
        state.files[self.filename] = new_content
        return f"File {self.filename} has been replaced."

    def __str__(self):
        return f"Function Called: {self.name()} filename={self.filename}, instructions={self.instructions}"
