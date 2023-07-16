import os

from gpt import gpt_query, GPT_4

SYSTEM_REPLACE = """
You are a helpful programming assistant. You will be given a list of files as well as instructions to modify them.
Please make ONLY the changes requested, and respond only with the changes in the format specified.

You should:

1) Start by using the @@THINK@@ command to explain your thinking
2) Request any information required that you don't already have
3) Only if all necessary information has been supplied, list updates to make
4) Always generate at least one command in the response

IF YOU UPDATE A FILE, INCLUDE ALL LINES. DO NOT LEAVE OUT ANY CONTENT, EVEN IF IT IS LONG.

Once you have made all modifications, always add a FINISH command at the end.

Do not add markdown quotes around code in your responses.

Requirements:
 * When moving code between files, ensure to add and remove import statements as required.
 * When deleting files, ensure that all references to it in other files are removed. 
 * Ignore python files not under src
 * When returning a file, indent it with tabs.

When finished, call the Verdict function and return to me the results.
"""


def replace_file(file, instructions):
    new_file = gpt_query(instructions, SYSTEM_REPLACE)
    return new_file
