from dataclasses import dataclass
from typing import List
import yaml
from tools.pytest import run_pytest


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
        result = run_pytest(f"{directory}/src", test_names)

        if result is not None:
            raise Exception(f"Pytest failed for tests: {test_names}\n{result}")
