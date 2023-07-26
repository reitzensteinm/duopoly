import json
from commands.command import Command
from gpt import gpt_query
from commands.state import State
from termcolor import cprint


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
    for command_class in command_classes:
        if command_class.name() == gpt_response["name"]:
            return command_class.load_from_json(json.loads(gpt_response["arguments"]))

    raise ValueError(f"Unrecognized command name: {gpt_response['name']}")


def command_loop_new(prompt: str, system: str, command_classes: list, files: dict = {}):
    state = State(files)
    exception_count = 0

    while True:
        try:
            result = gpt_query(
                prompt + "\n" + state.scratch, system, extract_schemas(command_classes)
            )

            if isinstance(result, str):
                return (result, state)

            command = parse_gpt_response(command_classes, result)

            if command.terminal:
                return (command, state)

            output = command.execute(state)

            state.scratch += "\n" + str(command)

            state.scratch += "\n" + output

            exception_count = 0
        except Exception as e:
            exception_count += 1
            cprint(f"Exception occurred: {str(e)}", "red")
            if exception_count >= 5:
                raise e
            else:
                print(
                    f"Retrying command execution, attempt number {exception_count+1}..."
                )
