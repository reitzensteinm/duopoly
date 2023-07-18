import os
import openai
import time
from utils import read_file, write_file, partition_by_predicate
from termcolor import cprint

GPT_3_5 = "gpt-3.5-turbo-0613"
GPT_4 = "gpt-4-0613"

SYSTEM_CHECK = "You are a helpful programming assistant. \
                You will be given original and modified versions of code. \
                If a file isn't present in the modified version, you can assume it was deleted. \
                You will also be given a description of the change that was intended. \
                Was the change that was made correct? \
                Please write a paragraph explaining your reasoning using this format: 'REASONING: <reasoning>'. \
                Afterwards, give a verdict, either by saying 'VERDICT: OK' or 'VERDICT: ERROR'. \
                This should be the last line of your response. \
                Are you absolutely sure? If you have any doubt at all, tell me there is an error. \
                If files aren't supplied, you can assume that their contents are correct. You are only checking issues in what you can see."

SYSTEM_CHECK_FUNC = "You are a helpful programming assistant. \
                    You will be given original and modified versions of code. \
                    If a file isn't present in the modified version, you can assume it was deleted. \
                    You will also be given a description of the change that was intended. \
                    Was the change that was made correct? \
                    Only respond by calling a function. \
                    Are you absolutely sure? If you have any doubt at all, tell me there is an error. \
                    If a file isn't supplied, always assume its content is completely correct."

SYSTEM_COMMAND_FUNC = """
You are a helpful programming assistant. You will be given a list of files as well as instructions to modify them.

Please make ONLY the changes requested, and respond only with the changes in the format specified.

You should:

1) Start by calling the think function with a step by step description of the changes you're about to make
2) Request any information required that you don't already have
3) Only if all necessary information has been supplied, list updates to make

Do not add markdown quotes around code in your responses.

Requirements:
 * When moving code between files, ensure to add and remove import statements as required.
 * When deleting files, ensure that all references to it in other files are removed. 
 * Ignore python files not under src
 * When returning a file, indent it with tabs.

When finished, call the Verdict function and return to me the results.
"""

from cache import memoize

disable_cache = True


def gpt_query(
    message: str,
    system: str,
    functions=None,
    model: str = GPT_4,
    require_function: bool = True,
) -> str:
    if model not in [GPT_4, GPT_3_5]:
        raise ValueError("Invalid model specified. Must be 'gpt-4' or 'gpt-3.5-turbo'.")

    openai.api_key = os.environ["OPENAI_API_KEY"]

    retries = 5
    backoff = 1

    for i in range(retries):
        try:
            start_time = time.time()
            cprint(f"GPT Input: {message}", "blue")
            messages = [
                {
                    "role": "system",
                    "content": system,
                },
                {"role": "user", "content": message},
            ]
            if functions is not None:
                completion = openai.ChatCompletion.create(
                    model=model, messages=messages, functions=functions
                )
            else:
                completion = openai.ChatCompletion.create(
                    model=model, messages=messages
                )

            if (
                functions is not None
                and "function_call" not in completion.choices[0].message
                and require_function
            ):
                cprint(
                    f"No functions returned. Message received: {completion.choices[0].message.content}",
                    "red",
                )
                raise Exception("No functions returned")

            end_time = time.time()
            call_duration = end_time - start_time

            tokens_in = completion["usage"]["prompt_tokens"]
            tokens_out = completion["usage"]["completion_tokens"]
            cprint(
                f"Call took {call_duration:.1f}s, {tokens_in} tokens in, {tokens_out} tokens out",
                "yellow",
            )

            break
        except Exception as e:
            if i == retries - 1:
                raise e

            time.sleep(backoff)
            backoff *= 2

    content = completion.choices[0].message.content
    if "function_call" in completion.choices[0].message:
        function_result = completion.choices[0].message["function_call"]
        cprint(
            f"Function call result: {function_result}", "cyan"
        )  # print function call result in cyan
        return function_result

    cprint(f"GPT Output: {content}", "cyan")
    return content


if not disable_cache:
    gpt_query = memoize(gpt_query)
