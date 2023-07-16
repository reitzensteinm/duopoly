import os

from gpt import gpt_query, GPT_4

SYSTEM_REPLACE = """
You are a helpful programming assistant. You will be given a file as well as instructions to modify it. 

Requirements:
1) Please make ONLY the changes requested.
2) Reply only with the updated file. 
3) Do not add markdown quotes around code in your responses. 
3) Use tabs to indentation."""


def modify_file(original_file, instructions):
    full_instructions = instructions + "\n" + original_file
    new_file = gpt_query(full_instructions, SYSTEM_REPLACE)
    return new_file
