import subprocess
import os


def run_pylint(directory: str, warnings: bool = False) -> str:
    if warnings:
        command = ["pylint", "--disable=R,C", directory]
    else:
        command = ["pylint", "--disable=R,C,W", directory]

    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return proc.stdout
    else:
        return None
