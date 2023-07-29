from gpt import cached_gpt_query
from gpt import GPT_4

SYSTEM_SUMMARIZE = """
Summarize the following source code, extracting classes, functions and constants by extracting the definitions into the following format:

# One line comment that describes the purpose of this class
class Test
   fn class_method(self)

# One line comment that describes the purpose of this function
fn a_function(arg1,arg2)

# One line comment that describes the purpose of this constant
CONSTANT_NAME
"""


def summarize(source_code: str) -> str:
    result = cached_gpt_query(source_code, system=SYSTEM_SUMMARIZE, model=GPT_4)
    return result
