# command_verdict.py
from commands.command import Command
from commands.state import State


class Verdict(Command):
    """
    Class representing a Verdict command.
    """

    @classmethod
    def name(cls) -> str:
        return "Verdict"

    @property
    def terminal(self):
        return True

    def __init__(self, reasoning: str, verdict: bool):
        self.reasoning: str = reasoning
        self.verdict: bool = verdict

    def __str__(self):
        return f"Function Called: {self.name()} reasoning={self.reasoning}, verdict={self.verdict}"

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Verdict command.
        """
        return {
            "name": "Verdict",
            "description": "Make a decision on whether the proposed change is acceptable or not",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": "Text that describes the reason for the supplied verdict",
                    },
                    "verdict": {
                        "type": "boolean",
                        "description": "A Boolean that describes whether or not the change is judged to be successful",
                    },
                },
                "required": ["reasoning", "verdict"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Verdict":
        """
        Loads the Verdict command from the provided json_data.
        """
        return Verdict(json_data["reasoning"], json_data["verdict"])

    def execute(self, state: State) -> tuple:
        """
        Executes the Verdict command.
        """
        return self.reasoning, self.verdict
