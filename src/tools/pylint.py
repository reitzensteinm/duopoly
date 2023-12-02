import subprocess
from typing import Optional
from tracing.trace import create_trace, bind_trace, trace
from tracing.tags import SYSTEM


def run_pylint(directory: str, warnings: bool = False) -> Optional[str]:
    """Run pylint on a given directory and return the processed output or None if no issues are found.

    This function takes a 'directory' parameter which is a string specifying the directory to be analyzed. The 'warnings' parameter, when set to True, includes warnings in the results. Returns a string containing the lint results with the directory replaced by 'src', or None if there are no lint issues.
    """
    trace_name: str = "pylint_trace"
    pylint_trace = create_trace(trace_name)
    bind_trace(pylint_trace)

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
        output: str = proc.stdout.replace(directory, "src")
        trace(SYSTEM, f"Pylint executed with output: {output}")
        return output
    else:
        trace(SYSTEM, f"Pylint executed with no issues found in {directory}")
        return None
