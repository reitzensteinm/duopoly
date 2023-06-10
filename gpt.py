import os
import openai
from utils import read_file, write_file, partition_by_predicate

SYSTEM_PATCH = "You are a helpful programming assistant. \
                You will be given code as well as instructions to modify it. \
                Please make ONLY the changes requested, and respond only with the changes in the format specified \
                and follow PEP-8 formatting standards. \
                The format for the patch should contain one line with start and end lines of the original file to replace, \
                followed by the new lines. Do not include the line numbers from the input. \
                Do not include any unnecessary blank lines in the patches. \
                RESPOND ONLY IN THE FOLLOWING FORMAT, AND DO NOT INCLUDE ANY OTHER COMMENTARY: \
                @@PATCH@@ <file name including relative path> <start-line> <end-line> \
                <new line 1>\
                <new line 2> ..."

SYSTEM_CHECK = "You are a helpful programming assistant. \
                You will be given original and modified versions of code. \
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

1) Request any information required that you don't already have
2) Only if all necessary information has been supplied, list updates to make

Respond with at least one command. The format is:

@@COMMAND@@ key1=value1 key2=value2
<body line 1>
<body line 2>

The commands available are:

Request the source code to a file:
@@FILE@@ path=<path>

Supply a new version of a file:
@@UPDATE@@ path=<path>
<file line 1>
<file line 2>

Indicate you're finished:
@@FINISH@@
"""

from cache import memoize


@memoize
def gpt_query(message: str, system: str = SYSTEM_PATCH) -> str:
    openai.api_key = os.environ["OPENAI_API_KEY"]

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system,
            },
            {"role": "user", "content": message},
        ],
    )

    content = completion.choices[0].message.content

    print(content)

    return content
