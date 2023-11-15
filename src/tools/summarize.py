from gpt import cached_gpt_query
from gpt import GPT_4
from utilities.prompts import load_prompt


def summarize(source_code: str) -> str:
    result = cached_gpt_query(
        source_code, system=load_prompt("summarize.txt"), model=GPT_4
    )
    return result
