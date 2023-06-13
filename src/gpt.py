import os
import openai
import time
from utils import read_file, write_file, partition_by_predicate
from termcolor import cprint

SYSTEM_PATCH = "You are a helpful programming assistant. \
                You will be given code as well as instructions to modify it. \
                Please make ONLY the changes requested, and respond only with the changes in the format specified \
                and follow PEP-8 formatting standards. \
                Read the STYLE file in order to understand the coding conventions of the project. \
                The format for the patch should contain one line with start and end lines of the original file to replace, \
                followed by the new lines. Do not include the line numbers from the input. \
                Do not include any unnecessary blank lines in the patches. \
                RESPOND ONLY IN THE FOLLOWING FORMAT, AND DO NOT INCLUDE ANY OTHER COMMENTARY: \
                @@PATCH@@ <file name including relative path> <start-line> <end-line> \
                <new line 1>\
                <new line 2> ..."

SYSTEM_CHECK = "You are a helpful programming assistant. \
                You will be given original and modified versions of code. \
                If a file isn't present in the modified version, you can assume it was deleted. \
                You will also be given a description of the change that was intended. \
                Was the change that was made correct? \
                Please write a paragraph explaining your reasoning using this format: 'REASONING: <reasoning>'. \
                Afterwards, give a verdict, either by saying 'VERDICT: OK' or 'VERDICT: ERROR'. \
                This should be the last line of your response. \
                Are you absolutely sure? If you have any doubt at all, tell me there is an error."

SYSTEM_COMMAND = """
You are a helpful programming assistant. You will be given a list of files as well as instructions to modify them.
Please make ONLY the changes requested, and respond only with the changes in the format specified.

You should:

1) Start by using the @@THINK@@ command to explain your thinking
2) Request any information required that you don't already have
3) Only if all necessary information has been supplied, list updates to make

IF YOU UPDATE A FILE, INCLUDE ALL LINES. DO NOT LEAVE OUT ANY CONTENT, EVEN IF IT IS LONG.

Once you have made all modifications, always add a FINISH command at the end.

Do not add markdown quotes around code in your responses.

When moving code between files, ensure to add and remove import statements as required.

Do not include anything in the response that is not a command. Respond with at least one command. The format is:

@@COMMAND@@ key1=value1 key2=value2
<body line 1>
<body line 2>

The commands available are:

Request the source code to a file:
@@FILE@@ path=<path>

Replace THE ENTIRE FILE with the specified lines:
@@UPDATE@@ path=<path>
<file line 1>
<file line 2>
...
<last line of file>

Delete a file:
@@DELETE@@ path=<path>

Announce you're finished:
@@FINISH@@

Think out loud about what you're about to do:
@@THINK@@
<thinking line 1>
<thinking line 2>

List imports contained in a file:
@@IMPORTS@@ path=<file>

When moving code between files, ensure to add and remove import statements as required.
"""

from cache import memoize


@memoize
def gpt_query(message: str, system: str = SYSTEM_PATCH, model: str = "gpt-4") -> str:
    if model not in ["gpt-4", "gpt-3.5-turbo"]:
        raise ValueError("Invalid model specified. Must be 'gpt-4' or 'gpt-3.5-turbo'.")

    openai.api_key = os.environ["OPENAI_API_KEY"]

    retries = 5
    backoff = 1

    for i in range(retries):
        try:
            cprint(f"GPT Input: {message}", "blue")
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system,
                    },
                    {"role": "user", "content": message},
                ],
            )
            break
        except Exception as e:
            if i == retries - 1:
                raise e

            time.sleep(backoff)
            backoff *= 2

    content = completion.choices[0].message.content

    cprint(f"GPT Output: {content}", "cyan")

    return content
