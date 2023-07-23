import os
from utilities.prompts import load_prompt
from gpt import gpt_query


def hydrate_code(source_code: str) -> str:
    prompt = load_prompt("hydrate")
    response = gpt_query(message=source_code, system=prompt)
    return response
