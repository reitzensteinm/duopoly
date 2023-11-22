from commands.command import Command
from commands.state import State


class Think(Command):
    """
    Class representing a Think command.
    """

    can_repeat = False

    @classmethod
    def name(cls) -> str:
        return "Think"

    @property
    def terminal(self):
        return False

    def __init__(self, thought: str, questions: str):
        self.thought: str = thought
        self.questions: str = questions

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
            "description": "Write out a plan for the steps you are about to take. Please think before taking any action. Include at least a paragraph of detail. It is important to ensure that the think command is not called more than once in succession to avoid redundant operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A description of what you plan to do in your next steps",
                    },
                    "questions": {
                        "type": "string",
                        "description": "List anything that is not clear about the instructions",
                    },
                },
                "required": ["thought", "questions"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Think":
        """
        Loads the Think command from the provided json_data.
        """
        return Think(json_data["thought"], json_data["questions"])

    def execute(self, state: State) -> str:
        """
        Executes the Think command.
        """
        return self.thought
