from gpt import gpt_query

SYSTEM_IMPORTS = """
Extract any imports from the following source code, returning only the lines that import other files.
"""


def imports(source_code: str) -> str:
    if not source_code.strip().endswith(".py"):
        return ""

    result = gpt_query(source_code, system=SYSTEM_IMPORTS, model="gpt-3.5-turbo")
    return result
