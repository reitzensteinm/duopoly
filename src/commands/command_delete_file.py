from commands.command import Command
from commands.state import State


class DeleteFile(Command):
    """
    Class representing DeleteFile command.
    """

    @classmethod
    def name(cls) -> str:
        return "DeleteFile"

    @property
    def terminal(self):
        return False

    def __init__(self, filename: str):
        self.filename: str = filename

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the DeleteFile command.
        """
        return {
            "name": "DeleteFile",
            "description": "Delete a specified file from the state",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to delete",
                    }
                },
                "required": ["filename"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "DeleteFile":
        """
        Loads the DeleteFile command from the provided json_data.
        """
        return DeleteFile(json_data["filename"])

    def execute(self, state: State):
        """
        Executes the DeleteFile command.
        """
        if self.filename in state.files:
            del state.files[self.filename]
            return f"File {self.filename} has been deleted."
        else:
            raise FileNotFoundError(
                f"Cannot delete file {self.filename} as it does not exist."
            )
