import os
from commands.command import Command
from commands.state import State
from tools.pip import install_package


class InstallPackage(Command):
    """
    Installs or updates a package to the latest version using pip.
    """

    @classmethod
    def name(cls) -> str:
        return "InstallPackage"

    @property
    def terminal(self):
        return False

    def __init__(self, tool: str):
        self.tool: str = tool

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the InstallPackage command.
        """
        return {
            "name": "InstallPackage",
            "description": "Install a tool using pip",
            "parameters": {
                "type": "object",
                "properties": {
                    "tool": {
                        "type": "string",
                        "description": "Name of the tool to be installed",
                    },
                },
                "required": ["tool"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "InstallPackage":
        """
        Loads the InstallPackage command from the provided json_data.
        """
        return InstallPackage(json_data["tool"])

    def execute(self, state: State):
        """
        Executes the InstallPackage command and ensures the package has been installed or updated and is on the latest version.
        """
        original_dir = os.getcwd()
        try:
            if state.target_dir:
                os.chdir(state.target_dir)
            requirements_contents = install_package(self.tool)
        finally:
            os.chdir(original_dir)

        state.files["requirements.txt"] = requirements_contents

        return f"Tool {self.tool} has been installed or updated and is on the latest version."

    def __str__(self):
        return f"Function Called: {self.name()} tool={self.tool}"
