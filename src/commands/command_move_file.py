from commands.command import Command
from commands.state import State
from tools.move_file import move_file


class MoveFile(Command):
    """
    Class representing MoveFile command.
    """

    @classmethod
    def name(cls) -> str:
        return "MoveFile"

    @property
    def terminal(self):
        return False

    def __init__(self, old_filename: str, new_filename: str):
        self.old_filename: str = old_filename
        self.new_filename: str = new_filename

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the MoveFile command.
        """
        return {
            "name": "MoveFile",
            "description": "Move a specified file from one location to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_filename": {
                        "type": "string",
                        "description": "Current path of the file",
                    },
                    "new_filename": {
                        "type": "string",
                        "description": "New path for the file",
                    },
                },
                "required": ["old_filename", "new_filename"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "MoveFile":
        """
        Loads the MoveFile command from the provided json_data.
        """
        return MoveFile(json_data["old_filename"], json_data["new_filename"])

    def execute(self, state: State):
        """
        Executes the MoveFile command.
        """
        if self.old_filename in state.files:
            try:
                state.files = move_file(
                    state.files, self.old_filename, self.new_filename
                )
                return (
                    f"File {self.old_filename} has been moved to {self.new_filename}."
                )
            except Exception as e:
                raise e
        else:
            raise FileNotFoundError(
                f"Cannot move file {self.old_filename} as it does not exist."
            )

    def __str__(self):
        return f"Function Called: MoveFile old_filename={self.old_filename} new_filename={self.new_filename}"
