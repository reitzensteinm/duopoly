import subprocess
from typing import Optional


def run_mypy(target_dir: str, use_strict: bool) -> Optional[str]:
    command = ["mypy", "--ignore-missing-imports"]

    if use_strict:
        command.append("--strict")

    command.append(target_dir)

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        return None

    return result.stderr.decode()
