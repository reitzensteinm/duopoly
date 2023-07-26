import os
from utilities.prompts import load_prompt
from gpt import gpt_query


def generate_advice(goal: str) -> str:
    prompt = load_prompt("advice.txt", {"goal": goal})
    response = gpt_query(
        message=prompt,
        system="Given the stated goal, return a list of the advice that is relevant",
    )
    return response