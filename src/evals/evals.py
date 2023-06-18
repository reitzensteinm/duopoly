from dataclasses import dataclass
from typing import List
import yaml


@dataclass
class Eval:
    prompt: str
    tests: List[str]


def process_evals(directory: str):
    with open(f"{directory}/prompts.yaml", "r") as file:
        data = yaml.safe_load(file)
        evals = [Eval(prompt=key, tests=value["tests"]) for key, value in data.items()]
