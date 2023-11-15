from .command import Command
from .state import State
from repo import revert_commits
from typing import List


class Revert(Command):
    """
    Class representing a Revert command.
    """

    @classmethod
    def name(cls) -> str:
        return "Revert"

    def __init__(self, commit_hashes: List[str]):
        self.commit_hashes: List[str] = commit_hashes

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Revert command.
        """
        return {
            "name": "Revert",
            "description": "Reverts a list of commit hashes in a repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "commit_hashes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The list of commit hashes to revert",
                    }
                },
                "required": ["commit_hashes"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Revert":
        """
        Loads the Revert command from the provided json_data.
        """
        return Revert(json_data["commit_hashes"])

    def execute(self, state: State) -> str:
        """
        Executes the Revert command.
        """
        try:
            revert_commits(self.commit_hashes, state.target_dir)
            return "Commits have been successfully reverted."
        except Exception as e:
            raise e

    def __str__(self):
        return f"Function Called: Revert commit_hashes={self.commit_hashes}"
