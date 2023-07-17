# command_search.py
from commands.command import Command
from commands.state import State


class Search(Command):
    """
    Class representing a Search command.
    """

    @classmethod
    def name(cls) -> str:
        return "Search"

    @property
    def terminal(self):
        return False

    def __init__(self, search_string: str):
        self.search_string: str = search_string

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Search command.
        """
        return {
            "name": "Search",
            "description": "Search for a specific string in the state's files",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_string": {
                        "type": "string",
                        "description": "The string to search for in the state's files",
                    }
                },
                "required": ["search_string"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Search":
        """
        Loads the Search command from the provided json_data.
        """
        return Search(json_data["search_string"])

    def execute(self, state: State) -> str:
        """
        Executes the Search command.
        """
        from tools.search import search_tool

        results = search_tool(state.files, self.search_string)
        return str(results)
