from gpt import cached_gpt_query, GPT_4

SYSTEM_SUMMARIZE = """
Summarize the following source code, extracting classes, functions and constants by extracting the definitions into the following format:

class Test
   fn class_method(self)

fn a_function(arg1,arg2)

CONSTANT
"""


def summarize(source_code: str) -> str:
    result = cached_gpt_query(source_code, system=SYSTEM_SUMMARIZE, model=GPT_4)
    return result
