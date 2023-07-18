import ast
import astor
from commands.command import Command
from commands.state import State
from utils import format_python_code


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
            "description": "Replace a specific node in a Python file",
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
        with open(self.filename, "r") as file:
            source_code = file.read()

        # Parse the source code into an AST
        tree = ast.parse(source_code)

        # Traverse the tree and find the node
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef)
            ) and node.name == self.node_name:
                # Parse new source code into an AST
                new_node = ast.parse(self.new_source_code).body[0]

                # Replace the node
                tree.body[tree.body.index(node)] = new_node

                # Break the loop after replacing the node, assuming there's no duplicate node
                break

        # Write the modified tree back to the source code
        modified_code = astor.to_source(tree)

        # Format the modified code
        formatted_code = format_python_code(modified_code)

        state.files[self.filename] = formatted_code

        return f"Node {self.node_name} in file {self.filename} has been replaced."

    def __str__(self):
        return (
            f"Function Called: {self.name()} filename={self.filename}, node_name={self.node_name}, "
            f"new_source_code={self.new_source_code}"
        )
