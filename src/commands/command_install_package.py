import os
from typing import List
from commands.command import Command
from commands.state import State
from tools.pip import install_package


class InstallPackage(Command):
    """
    Installs or updates packages to the latest versions using pip.
    """

    @classmethod
    def name(cls) -> str:
        return "InstallPackage"

    @property
    def terminal(self):
        return False

    def __init__(self, tools: List[str]):
        self.tools: List[str] = tools

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the InstallPackage command.
        """
        return {
            "name": "InstallPackage",
            "description": "Install multiple tools using pip",
            "parameters": {
                "type": "object",
                "properties": {
                    "tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Names of the tools to be installed",
                    },
                },
                "required": ["tools"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "InstallPackage":
        """
        Loads the InstallPackage command from the provided json_data.
        """
        return InstallPackage(json_data["tools"])

    def execute(self, state: State):
        """
        Executes the InstallPackage command and ensures the packages have been installed or updated and are on the latest versions.
        """
        original_dir = os.getcwd()
        requirements_contents = ""
        try:
            if state.target_dir:
                os.chdir(state.target_dir)
            for tool in self.tools[:-1]:
                install_package(tool)
            if self.tools:
                requirements_contents = install_package(self.tools[-1])
        finally:
            os.chdir(original_dir)

        state.files["requirements.txt"] = requirements_contents

        return f"Tools have been installed or updated and are on the latest versions."

    def __str__(self):
        tools_str = ", ".join(self.tools)
        return f"Function Called: {self.name()} tools=[{tools_str}]"
