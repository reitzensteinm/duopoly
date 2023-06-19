from dataclasses import dataclass
from typing import List
import yaml
import subprocess


@dataclass
class Eval:
    prompt: str
    tests: List[str]


def process_evals(directory: str):
    with open(f"{directory}/prompts.yaml", "r") as file:
        data = yaml.safe_load(file)
        evals = [Eval(prompt=key, tests=value["tests"]) for key, value in data.items()]

    for eval in evals:
        test_names = " ".join(eval.tests)
        result = subprocess.run(
            ["pytest", f"{directory}/src", "-k", test_names],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise Exception(f"Pytest failed for tests: {test_names}\n{result.stderr}")
