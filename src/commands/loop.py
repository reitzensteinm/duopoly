import json
from commands.command import Command, parse_gpt_response
from gpt import gpt_query


def command_loop(prompt: str, system: str, command_classes: list):
    while True:
        result = gpt_query(prompt, system, command_classes)
        command = parse_gpt_response(command_classes, json.loads(result))

        if command.terminal:
            return command

        output = command.execute()
        prompt += "\n" + output
