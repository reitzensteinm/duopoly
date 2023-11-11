import subprocess
from .command import Command
from .state import State
from tracing.trace import trace
from tracing.tags import SYSTEM


class Terminal(Command):
    """
    Class representing a Terminal command.
    """

    @classmethod
    def name(cls) -> str:
        return "Terminal"

    @property
    def terminal(self):
        """
        A property that indicates whether the command should terminate the sequence when executed.
        This returns False as executing a command on the console does not necessarily mean
        the end of the command sequence.
        """
        return False

    def __init__(self, command_string: str):
        self.command_string: str = command_string

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Terminal command.
        """
        return {
            "name": "Terminal",
            "description": "Execute a given string as a terminal command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command_string": {
                        "type": "string",
                        "description": "The terminal command to execute",
                    }
                },
                "required": ["command_string"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Terminal":
        """
        Loads the Terminal command from the provided json_data.
        """
        return Terminal(json_data["command_string"])

    def execute(self, state: State) -> str:
        """
        Executes the Terminal command.
        """
        trace(SYSTEM, f"Executing terminal command: {self.command_string}")
        result = subprocess.run(
            self.command_string, shell=True, capture_output=True, text=True
        )
        trace(SYSTEM, f"Terminal command output: {result.stdout}")
        return result.stdout

    def __str__(self):
        return f"Function Called: Terminal command_string={self.command_string}"
