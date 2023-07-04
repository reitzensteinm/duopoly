import json
from commands.state import State

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


class Think(Command):
    """
    Class representing a Think command.
    """

    @classmethod
    def name(cls) -> str:
        return "Think"

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

    def execute(self, state: State) -> str:
        """
        Executes the Think command.
        """
        return self.thought


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
                result += f"{file}: \n{state.files[file]}"
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

    def __init__(self, filename: str, content: str):
        self.filename: str = filename
        self.content: str = content

    @staticmethod
    def schema() -> dict:
        """
        Returns the schema for the ReplaceFile command.
        """
        return {
            "name": "ReplaceFile",
            "description": "Replace the content of a file in the state",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to be replaced",
                    },
                    "content": {
                        "type": "string",
                        "description": "The new content of the file",
                    },
                },
                "required": ["filename", "content"],
            },
        }

    @staticmethod
    def load_from_json(json_data: dict) -> "ReplaceFile":
        """
        Loads the ReplaceFile command from the provided json_data.
        """
        return ReplaceFile(json_data["filename"], json_data["content"])

    def execute(self, state: State):
        """
        Executes the ReplaceFile command.
        """
        state.files[self.filename] = self.content
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

    def execute(self, state: State) -> list:
        """
        Executes the Search command.
        """
        from tools.search import search_tool

        results = search_tool(state.files, self.search_string)
        return results


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


commands: list = [Think, Verdict, Files, ReplaceFile, Search, DeleteFile]


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
        if command_class.name() == gpt_response["name"]:
            return command_class.load_from_json(json.loads(gpt_response["arguments"]))

    raise ValueError(f"Unrecognized command name: {gpt_response['name']}")
