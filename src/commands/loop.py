import json
from commands.command import Command, parse_gpt_response
from gpt import gpt_query
from commands.state import State


def command_loop(prompt: str, system: str, command_classes: list, files: dict = {}):
    state = State(files)
    while True:
        result = gpt_query(prompt + "\n" + state.scratch, system, command_classes)
        command = parse_gpt_response(command_classes, json.loads(result))

        if command.terminal:
            return command

        output = command.execute()
        state.scratch += "\n" + output
