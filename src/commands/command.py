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


class Files(Command):
    """
    Class representing a Files command.
    """

    @classmethod
    def name(cls) -> str:
        return "Files"

    @property
    def terminal(self):
        return False

    def __init__(self, files: list):
        self.files: list = files

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the Files command.
        """
        return {
            "name": "Files",
            "description": "List files and their contents from the state",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "description": "List of files to retrieve",
                        "items": {"type": "string"},
                    }
                },
                "required": ["files"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "Files":
        """
        Loads the Files command from the provided json_data.
        """
        return Files(json_data["files"])

    def execute(self, state: State) -> str:
        """
        Executes the Files command.
        """
        result = ""
        for file in self.files:
            if file in state.files:
                annotated_content = annotate_with_line_numbers(state.files[file])
                result += f"{file}: \n{annotated_content}"
        return result


class ReplaceFile(Command):
    """
    Class representing ReplaceFile command.
    """

    @classmethod
    def name(cls) -> str:
        return "ReplaceFile"

    @property
    def terminal(self):
        return False

    def __init__(self, filename: str, instructions: str):
        self.filename: str = filename
        self.instructions: str = instructions

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the ReplaceFile command.
        """
        return {
            "name": "ReplaceFile",
            "description": "Modify a file with the given instructions",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to be replaced",
                    },
                    "instructions": {
                        "type": "string",
                        "description": "Human readable description for how the file should be modified, without code",
                    },
                },
                "required": ["filename", "instructions"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "ReplaceFile":
        """
        Loads the ReplaceFile command from the provided json_data.
        """
        return ReplaceFile(json_data["filename"], json_data["instructions"])

    def execute(self, state: State):
        """
        Executes the ReplaceFile command.
        """
        new_content = modify_file(
            state.files.get(self.filename, ""), self.instructions, state.scratch
        )
        if self.filename.endswith(".py"):  # Check if it's a Python file
            new_content = format_python_code(
                new_content
            )  # Format the content if it's a Python file
        state.files[self.filename] = new_content
        return f"File {self.filename} has been replaced."


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


class DeleteFile(Command):
    """
    Class representing DeleteFile command.
    """

    @classmethod
    def name(cls) -> str:
        return "DeleteFile"

    @property
    def terminal(self):
        return False

    def __init__(self, filename: str):
        self.filename: str = filename

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the DeleteFile command.
        """
        return {
            "name": "DeleteFile",
            "description": "Delete a specified file from the state",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to delete",
                    }
                },
                "required": ["filename"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "DeleteFile":
        """
        Loads the DeleteFile command from the provided json_data.
        """
        return DeleteFile(json_data["filename"])

    def execute(self, state: State):
        """
        Executes the DeleteFile command.
        """
        if self.filename in state.files:
            del state.files[self.filename]
            return f"File {self.filename} has been deleted."
        else:
            raise FileNotFoundError(
                f"Cannot delete file {self.filename} as it does not exist."
            )
