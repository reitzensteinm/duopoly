import ast
import astor
from commands.command import Command
from commands.state import State
from utils import format_python_code
from tools.code import replace_node


class ReplaceNode(Command):
    """
    Class representing ReplaceNode command.
    """

    @classmethod
    def name(cls) -> str:
        return "ReplaceNode"

    @property
    def terminal(self):
        return False

    def __init__(self, filename: str, node_name: str, new_source_code: str):
        self.filename: str = filename
        self.node_name: str = node_name
        self.new_source_code: str = new_source_code

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the ReplaceNode command.
        """
        return {
            "name": "ReplaceNode",
            "description": "Replace a specific node in a Python file. This command returns a special token for the new node.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the Python file",
                    },
                    "node_name": {
                        "type": "string",
                        "description": "Name of the node (class or function) to be replaced",
                    },
                    "new_source_code": {
                        "type": "string",
                        "description": "New source code to replace the node",
                    },
                },
                "required": ["filename", "node_name", "new_source_code"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "ReplaceNode":
        """
        Loads the ReplaceNode command from provided json_data.
        """
        return ReplaceNode(
            json_data["filename"], json_data["node_name"], json_data["new_source_code"]
        )

    def execute(self, state: State):
        """
        Executes the ReplaceNode command.
        """
        source_code = state.files[self.filename]

        # Update the source code using the replace_node tool
        modified_code = replace_node(source_code, self.node_name, self.new_source_code)

        # Format the modified code
        formatted_code = format_python_code(modified_code)

        state.files[self.filename] = formatted_code

        return f"Node {self.node_name} in file {self.filename} has been replaced."

    def __str__(self):
        return (
            f"Function Called: {self.name()} filename={self.filename}, node_name={self.node_name}, "
            f"new_source_code={self.new_source_code}"
        )
