import os
import subprocess
import shutil


def run_pytest(target_dir):
    try:
        result = subprocess.run(
            ["pytest", target_dir, "-rf"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return None
        else:
            return result.stdout
    except Exception as e:
        return str(e)
