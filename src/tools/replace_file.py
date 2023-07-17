from gpt import gpt_query

SYSTEM_REPLACE_THINK = """
You are a helpful programming assistant. You will be given a file as well as instructions to modify it.

Plan out step by step how you'd like to make the change, but don't start writing code yet. 
You will be asked to write code in the next step.

An example plan might be:

1) Modify function count_functions to also count classes
2) Throw an exception when an unterminated string is passed to parse_file
"""

SYSTEM_REPLACE = """
You are a helpful programming assistant. You will be given a file as well as instructions to modify it. 

Requirements:
1) Please make ONLY the changes requested.
2) Reply only with the updated file. Do not include any commentary. 
3) Do not add markdown quotes around code in your responses. 
4) Use tabs for indentation.
5) Do not add any tests unless specifically requested.
6) Return the entire file without skipping anything or stopping before the end, no matter how long it is. 
7) Do not include line numbers in your output.
8) Include content from only the file specified.
9) Do not include the file name or any other content that should not be included in the file itself.
"""


def modify_file(original_file, instructions, context=""):
    instructions = f"### CONTEXT ###\n{context}\n### INSTRUCTIONS ###\n{instructions}\n### ORIGINAL FILE ###\n(see context)\n### THINKING ###"
    thinking = gpt_query(instructions, SYSTEM_REPLACE_THINK)
    instructions = f"{instructions}\n{thinking}\n### NEW FILE ###"
    new_file = gpt_query(instructions, SYSTEM_REPLACE)
    return new_file
