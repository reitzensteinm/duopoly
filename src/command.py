"""
Commands in Python are stored as dicts. The "command" key stores the id of the key. The optional "body" key stores the body of the command. All other keys are a key/value pair, which are all string/strings.

In text, the format of a command is as follows:

@@COMMAND_ID@@ key_a=value_a key_b=value_b
OPTIONAL
BODY
OVER
MULTIPLE
LINES
"""


def command_to_str(command: dict) -> str:
    formatted_command = f"@@{command['command']}@@"
    for key, value in command.items():
        if key not in ["command", "body"]:
            formatted_command += f" {key}={value}"
    if "body" in command:
        formatted_lines = "\n".join(
            [f"{line}" for line in command["body"].splitlines()]
        )
        formatted_command += f"\n{formatted_lines}"
    return formatted_command


def parse_command_string(command_string: str) -> list[dict]:
    command_list = []
    inside_multiline_string = False
    found_first_command = False

    for line in command_string.split("\n"):
        if '"""' in line:
            inside_multiline_string = not inside_multiline_string

        if not inside_multiline_string and line.startswith("@@"):
            found_first_command = True
            idx = line.index("@@", 2)
            command_id = line[2:idx]

            command_values = line[idx + 2 :].split(" ")
            command_dict = {"command": command_id}

            for item in command_values:
                if item:  # Ignore empty string
                    key, value = item.split("=")
                    command_dict[key] = value

            command_list.append(command_dict)
        elif found_first_command:
            command_list[-1].setdefault("body", []).append(line)

    for command in command_list:
        if "body" in command:
            command["body"] = "\n".join(command["body"])

    return command_list
