import os

from gpt import gpt_query, GPT_4

SYSTEM_REPLACE = """
You are a helpful programming assistant. You will be given a list of files as well as instructions to modify them.
Please make ONLY the changes requested, and respond only with the changes in the format specified.

Once you have made all modifications, always add a FINISH command at the end.

Do not add markdown quotes around code in your responses.

When finished, call the Verdict function and return to me the results.
"""


def modify_file(file, instructions, original_file):
    full_instructions = instructions + "\n" + original_file
    new_file = gpt_query(full_instructions, SYSTEM_REPLACE)
    return new_file
