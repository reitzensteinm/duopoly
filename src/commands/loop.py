import json
from commands.command import Command, parse_gpt_response, extract_schemas
from gpt import gpt_query
from commands.state import State
from termcolor import cprint


def stringify_command(command: Command) -> str:
    """Converts the command into a string representation."""
    parameters_string = ""

    # Handling specific command types
    if type(command).__name__ == "Think":
        parameters_string = f"thought={command.thought}"
    elif type(command).__name__ == "Files":
        parameters_string = f"files={command.files}"
    elif type(command).__name__ == "ReplaceFile":
        # Include actual 'filename' and 'content' from the 'ReplaceFile' command
        parameters_string = f"filename={command.filename}, content={command.content}"
    elif type(command).__name__ == "Search":
        parameters_string = f"search_string={command.search_string}"
    elif type(command).__name__ == "DeleteFile":
        parameters_string = f"filename={command.filename}"
    elif type(command).__name__ == "Verdict":
        parameters_string = f"reasoning={command.reasoning}, verdict={command.verdict}"

    return f"Function Called: {command.name()} {parameters_string}"


def command_loop_new(prompt: str, system: str, command_classes: list, files: dict = {}):
    state = State(files)
    exception_count = 0

    while True:
        try:
            result = gpt_query(
                prompt + "\n" + state.scratch, system, extract_schemas(command_classes)
            )
            result["arguments"] = result["arguments"].replace("\t", "\\t")
            command = parse_gpt_response(command_classes, result)

            if command.terminal:
                return (command, state)

            # Adding stringified command to scratch
            state.scratch += "\n" + stringify_command(command)

            output = command.execute(state)
            state.scratch += "\n" + output

            # If command execute successfully, reset the exception counter
            exception_count = 0
        except Exception as e:
            exception_count += 1
            cprint(f"Exception occurred: {str(e)}", "red")
            if exception_count >= 5:
                break
            else:
                print(
                    f"Retrying command execution, attempt number {exception_count+1}..."
                )
