import subprocess
from typing import Optional
from tracing.trace import trace
from tracing.tags import SYSTEM


def run_pylint(directory: str, warnings: bool = False) -> Optional[str]:
    """Run pylint on a given directory and return the processed output or None if no issues are found.

    This function takes a 'directory' parameter which is a string specifying the directory to be analyzed. The 'warnings' parameter, when set to True, includes warnings in the results. Returns a string containing the lint results with the directory replaced by 'src', or None if there are no lint issues.
    """
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
        trace(SYSTEM, proc.stdout)
        return proc.stdout.replace(directory, "src")
    else:
        return None
