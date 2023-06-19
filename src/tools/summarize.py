from gpt import gpt_query, GPT_3_5

SYSTEM_SUMMARIZE = """
Summarize the following source code, extracting classes, functions and constants by extracting the definitions into the following format:

class Test
   fn class_method(self)

fn a_function(arg1,arg2)

CONSTANT
"""


def summarize(source_code: str) -> str:
    result = gpt_query(source_code, system=SYSTEM_SUMMARIZE, model=GPT_3_5)
    return result
