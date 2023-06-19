from gpt import gpt_query, GPT_3_5

SYSTEM_IMPORTS = """
Extract any imports from the following source code, returning only the lines that import other files.
"""


def imports(source_code: str) -> str:
    result = gpt_query(source_code, system=SYSTEM_IMPORTS, model=GPT_3_5)
    return result
