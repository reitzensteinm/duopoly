import json

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

    @property
    def terminal(self):
        """
        Whether or not this command is a terminal command.
        """
        raise NotImplementedError

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

    @property
    def terminal(self):
        return False

    def __init__(self, thought: str):
        self.thought: str = thought

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

    @property
    def terminal(self):
        return True

    def __init__(self, reasoning: str, verdict: bool):
        self.reasoning: str = reasoning
        self.pass_verdict: bool = verdict

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

    def execute(self) -> tuple:
        """
        Executes the Verdict command.
        """
        return self.reasoning, self.pass_verdict


commands: list = [Think, Verdict]


def extract_schemas(command_classes):
    """
    Extracts schemas from a list of command classes.
    """
    schemas = [command_class.schema() for command_class in command_classes]
    return schemas


def parse_gpt_response(command_classes, gpt_response):
    """
    Parses the response from GPT and returns a Command instance for that response.
    """
    # i.e. GPT response looks like:
    # {
    #   "arguments": "{\n\"reasoning\": \"Yes, the change is correct. The result of 1+1 is indeed 2. The expression has been simplified correctly.\",\n\"verdict\": true\n}",
    #   "name": "Verdict"
    # }
    for command_class in command_classes:
        if command_class.name == gpt_response["name"]:
            return command_class.load_from_json(json.loads(gpt_response["arguments"]))

    raise ValueError(f"Unrecognized command name: {gpt_response['name']}")
