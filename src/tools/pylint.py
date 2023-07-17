import subprocess
import os


def run_pylint(directory: str) -> str:
    proc = subprocess.run(
        ["pylint", "--disable=R,C,W", os.path.join(directory, "src")],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return proc.stdout
    else:
        return None
