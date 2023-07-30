# src/commands/command_plan.py

from commands.command import Command
from commands.state import State


class Plan(Command):
    """
    Class representing a Plan command.
    """

    @classmethod
    def name(cls) -> str:
        return "Plan"

    @property
    def terminal(self):
        return False

    def __init__(self, thought: str, steps: list):
        self.thought: str = thought
        self.steps: list = steps

    def __str__(self):
        """
        Returns a string representation of the Plan command.
        """
        return f"Function Called: Plan thought={self.thought}, steps={self.steps}"

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Plan command.
        """
        return {
            "name": "Plan",
            "description": "Plan out the changes, breaking down the changes required to files, classes or functions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A description of what you plan to do in your next steps",
                    },
                    "steps": {
                        "type": "array",
                        "description": "A one paragraph description of a change we want to make to a file, function or class.",
                    },
                },
                "required": ["thought", "steps"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Plan":
        """
        Loads the Plan command from the provided json_data.
        """
        steps = json_data.get("steps", [])
        return Plan(json_data["thought"], steps)

    def execute(self, state: State) -> str:
        """
        Executes the Plan command.
        """
        return self.thought, self.steps
