from utilities.prompts import load_prompt
from gpt import gpt_query


def hydrate_code(source_code: str) -> str:
    """Hydrates the provided source code using AI-driven suggestions.

    Args:
    source_code: The code to be hydrated, as a string.

    Returns:
    The hydrated source code, as a string.
    """
    prompt = load_prompt("hydrate")
    response = gpt_query(message=source_code, system=prompt)
    return response
