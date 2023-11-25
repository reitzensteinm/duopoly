import json
from commands.state import State
from gpt import gpt_query, gpt_query_tools
from settings import get_settings
from termcolor import cprint


def extract_schemas(command_classes: list) -> list:
    """
    Extracts and returns the schema from each command class in the provided list.

    Args: command_classes (list): List of command classes to inspect.
    Returns: List of schema dictionaries for the commands.
    """
    schemas = [command_class.schema() for command_class in command_classes]
    return schemas


def parse_gpt_response(command_classes: list, gpt_response: "GPTResponse") -> "Command":
    """
    Parses a GPT response and returns a corresponding Command instance.

    Args:
            command_classes: A list of command classes to match the GPT response against.
            gpt_response: The GPT response containing the name of the command and its arguments.
    Returns:
            An instance of the Command that corresponds to the GPT response.
    Raises:
            ValueError: If the command name from GPT response is not recognized.
    """
    for command_class in command_classes:
        if command_class.name() == gpt_response.name:
            return command_class.load_from_json(json.loads(gpt_response.arguments))
    raise ValueError(f"Unrecognized command name: {gpt_response.name}")


def command_loop_iterate(state: State, system: str, command_classes: list) -> tuple:
    """
    Processes a command loop iteration.

    This function processes a single iteration of the command loop, handling the execution
    of a command based on the GPT-generated responses and updates the state accordingly.
    The function supports processing multiple results, but currently, GPT queries return a single result.

    Args:
            state (State): The current state of the command loop.
            system (str): The GPT-3 system being used.
            command_classes (list): A list of available command classes.
    Returns:
            tuple: A tuple containing execution results and the updated state.
    """
    if (
        state.last_command
        and hasattr(state.last_command, "can_repeat")
        and state.last_command.can_repeat
    ):
        pass
    else:
        command_classes = [
            cmd_cls
            for cmd_cls in command_classes
            if cmd_cls != state.last_command.__class__
        ]
    temp_scratch = state.scratch + "\n\n" + state.render_information()
    try:
        if get_settings().use_tools:
            cprint("Using experimental tools feature", "red")
            results = gpt_query_tools(
                temp_scratch + "\n", system, extract_schemas(command_classes)
            )
        else:
            result = gpt_query(
                temp_scratch + "\n", system, extract_schemas(command_classes)
            )
            if isinstance(result, str):
                return result, state
            results = [result]

        for result in results:
            command = parse_gpt_response(command_classes, result)
            if command.terminal:
                return command, state
            output = command.execute(state)
            state.scratch += "\n" + str(command)
            state.scratch += "\n" + output
            state.last_command = command
        return None, state
    except Exception as e:
        state.scratch += "\nException thrown calling command! " + str(e)
        return None, state


def command_loop(
    prompt: str,
    system: str,
    command_classes: list,
    files: dict = {},
    target_dir: str = None,
) -> (str, State):
    """
    Initiates a command loop where GPT can iteratively execute a series of commands based on user prompts.

    Args:
            prompt: The initial prompt to start the command loop.
            system: The system which is used for GPT querying.
            command_classes: A list of Command classes available for execution.
            files: An optional dictionary of file names to file contents.
            target_dir: An optional target directory for file operations.
    Returns:
            A tuple containing any terminal output as a string and the final state.
    """
    state = State(files, target_dir=target_dir)
    state.scratch = prompt
    state.last_command_instance = None
    exception_count = 0
    while True:
        try:
            result, state = command_loop_iterate(state, system, command_classes)
            if result is not None:
                return result, state
        except Exception as e:
            exception_count += 1
            cprint(f"Exception occurred: {str(e)}", "red")
            if exception_count >= 5:
                raise e
            else:
                print(
                    f"Retrying command execution, attempt number {exception_count + 1}..."
                )
