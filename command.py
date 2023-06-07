def command_to_str(command: dict) -> str:
    formatted_command = f"@@{command['command']}@@"
    if "response" in command:
        formatted_command = f"> {formatted_command}"
    for key, value in command.items():
        if key not in ["command", "body", "response"]:
            formatted_command += f" {key}={value}"
    if "body" in command:
        formatted_lines = "\n".join(
            [f"> {line}" for line in command["body"].splitlines()]
        )
        formatted_command += f"\n{formatted_lines}"
    return formatted_command


def parse_command_string(command_string: str) -> list[dict]:
    command_list = []
    response_flag = False

    for line in command_string.split("\n"):
        if line.startswith("> @@"):
            response_flag = True
            line = line[2:].lstrip()

        if line.startswith("@@") and line.endswith("@@"):
            idx = line.index("@@", 2)
            command_id = line[2:idx]

            command_values = line[idx + 2 :].split(" ")
            command_dict = {"command": command_id}

            for item in command_values:
                key, value = item.split("=")
                command_dict[key] = value

            command_list.append(command_dict)
        elif line.startswith(">"):
            body_line = line[1:].lstrip()
            command_list[-1].setdefault("body", []).append(body_line)
        else:
            if not response_flag:
                if command_list[-1].get("body"):
                    command_list[-1]["body"] = "\n".join(command_list[-1]["body"])
                command_list[-1]["response"] = line
    return command_list
