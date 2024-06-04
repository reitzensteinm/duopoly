from ..gpt import cached_gpt_query, GPT_4
from utilities.prompts import load_prompt


def summarize(source_code: str) -> str:
    """
    Generate a summary for the given source code by querying the cached GPT model with the source code as input.

    Argument:
    source_code: A str containing the source code to be summarized.

    Returns:
    A str containing the summary of the provided source code.
    """
    result = cached_gpt_query(
        source_code, system=load_prompt("summarize.txt"), model=GPT_4
    )
    return result
