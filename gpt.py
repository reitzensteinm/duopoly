import os
import openai
from utils import read_file, write_file, partition_by_predicate


def gpt_query(message: str) -> str:
    """Sends a message to GPT-4 and returns the response."""
    openai.api_key = os.environ["OPENAI_API_KEY"]

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful programming assistant. \
                You will be given code as well as instructions to modify it. \
                Please make ONLY the changes requested, and respond only with the changes in the format specified \
                and follow PEP-8 formatting standards. \
                The format for the patch should contain one line with start and end lines of the original file to replace, \
                followed by the new lines. Do not include the line numbers from the input. \
                Do not include any unnecessary blank lines in the patches. \
                RESPOND ONLY IN THE FOLLOWING FORMAT, AND DO NOT INCLUDE ANY OTHER COMMENTARY: \
                @@PATCH@@ <file name including relative path> <start-line> <end-line> \
                <new line 1>\
                <new line 2> ...",
            },
            {"role": "user", "content": message},
        ],
    )

    return completion.choices[0].message.content
