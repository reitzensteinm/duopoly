from commands.command import Command
from commands.state import State
from utils import annotate_with_line_numbers


def replace_spaces_with_tabs(content: str) -> str:
    """
    Replaces 4 spaces at the beginning of each line with tabs.
    """
    lines = content.split("\n")
    modified_lines = []
    for line in lines:
        leading_spaces = len(line) - len(line.lstrip(" "))
        if leading_spaces % 4 == 0:
            tabs = leading_spaces // 4
            modified_line = "\t" * tabs + line.lstrip(" ")
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)
    return "\n".join(modified_lines)


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
        self.files: list = [
            (file[2:] if file.startswith("./") else file) for file in files
        ]

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

    def __str__(self):
        """
        Returns a string representation of the Files command.
        """
        return f"Function Called: Files files={self.files}"

    def execute(self, state: State) -> str:
        """
        Executes the Files command.
        Adds line numbers to the file contents.

        Args:
                state (State): The current state object.

        Returns:
                str: Messages indicating the status of each file.
        """
        messages = []
        for file in self.files:
            if file in state.files:
                content_with_tabs = replace_spaces_with_tabs(state.files[file])
                annotated_content = annotate_with_line_numbers(content_with_tabs)
                state.information[file] = annotated_content
                messages.append(f"File {file} has been added to context")
            else:
                messages.append(f"File {file} does not exist.")
        return "\n".join(messages)
