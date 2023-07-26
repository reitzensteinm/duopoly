import os
from utilities.prompts import load_prompt
from gpt import gpt_query


def generate_advice(goal: str) -> str:
    prompt = load_prompt("advice", {"goal": goal})
    response = gpt_query(
        message=prompt,
        system="Given the stated goal, return a list of the advice that is relevant. Do not add new advice. Just return a list of the supplied advice verbatim that is relevant to the stated goal.",
    )
    return response
