"""
Example Command schema:
{
    "name": "get_current_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA",
            },
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["location"],
    }
}
"""


class Command:
    """
    Class representing a command.
    """

    name: str = ""

    def __init__(self):
        pass

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the command.
        """
        return {}

    @staticmethod
    def load_from_json(json_data: dict):
        """
        Loads the command from the provided json_data.
        """
        pass

    def execute(self):
        """
        Executes the command.
        """
        pass


class Think(Command):
    """
    Class representing a Think command.
    """

    name: str = "Think"

    def __init__(self, thought: str):
        self.thought: str = thought

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Think command.
        """
        return {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "A description of what you plan to do in your next steps",
                }
            },
            "required": ["thought"],
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Think":
        """
        Loads the Think command from the provided json_data.
        """
        return Think(json_data["thought"])

    def execute(self) -> str:
        """
        Executes the Think command.
        """
        return self.thought


class Verdict(Command):
    """
    Class representing a Verdict command.
    """

    name: str = "Verdict"

    def __init__(self, reasoning: str, verdict: bool):
        self.reasoning: str = reasoning
        self.pass_verdict: bool = verdict

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Verdict command.
        """
        return {
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
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Verdict":
        """
        Loads the Verdict command from the provided json_data.
        """
        return Verdict(json_data["reasoning"], json_data["verdict"])

    def execute(self) -> tuple:
        """
        Executes the Verdict command.
        """
        return self.reasoning, self.pass_verdict


commands: list = [Think, Verdict]
