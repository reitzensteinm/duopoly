import json
from tools.replace_file import modify_file
from commands.state import State
from utils import annotate_with_line_numbers, format_python_code
from black import (
    FileMode,
    format_str,
)  # Added import for Black's format_str and FileMode

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

    @classmethod
    def name(cls) -> str:
        """
        Returns the name of the command.
        This should be overridden by subclasses if needed.
        """
        return ""

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

    def execute(self, state: State):
        """
        Executes the command.
        """
        pass
