import os
import subprocess
import shutil


def run_pytest(target_dir, test_name=None):
    try:
        command_list = ["pytest", target_dir, "-rf"]
        if test_name is not None:
            command_list = ["pytest", target_dir, "-k", test_name, "-rf"]

        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return None
        else:
            return result.stdout
    except Exception as e:
        return str(e)
