import subprocess
from typing import Optional
from tracing.trace import Trace
from tracing.tags import SYSTEM


def run_pylint(directory: str, warnings: bool = False) -> Optional[str]:
    """Run pylint on a given directory, create a trace if issues are found, and return the processed output or None.

    This function takes a 'directory' parameter to specify the directory to be analyzed and a 'warnings' boolean to include warnings in the results. If pylint finds issues, it records a trace tagged with 'SYSTEM' and returns the results with the directory replaced by 'src'. It returns None if there are no issues.
    """
    trace = Trace("pylint")
    if warnings:
        command = ["pylint", "--disable=R,C", directory]
    else:
        command = ["pylint", "--disable=R,C,W", directory]

    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    output = proc.stdout.replace(directory, "src")
    if proc.returncode != 0:
        trace.add_trace_data(SYSTEM, output)
        return output
    else:
        return None
