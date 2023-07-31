# src/commands/command_think.py

from commands.command import Command
from commands.state import State


class Think(Command):
    """
    Class representing a Think command.
    """

    @classmethod
    def name(cls) -> str:
        return "Think"

    @property
    def terminal(self):
        return False

    def __init__(self, thought: str):
        self.thought: str = thought

    def __str__(self):
        """
        Returns a string representation of the Think command.
        """
        return "Function Called: Think"

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Think command.
        """
        return {
            "name": "Think",
            "description": "Write out a plan for the steps you are about to take. Please think before taking any action. Include at least a paragraph of detail",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A description of what you plan to do in your next steps",
                    }
                },
                "required": ["thought"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Think":
        """
        Loads the Think command from the provided json_data.
        """
        return Think(json_data["thought"])

    def execute(self, state: State) -> str:
        """
        Executes the Think command.
        """
        return self.thought
