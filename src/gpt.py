import os
import openai
import time
from utils import read_file, write_file, partition_by_predicate
from termcolor import cprint
from tracing.trace import trace
from tracing.tags import GPT_INPUT, GPT_OUTPUT
from cache import memoize
from utilities.prompts import load_prompt

GPT_3_5 = "gpt-3.5-turbo-0613"
GPT_4 = "gpt-4-0613"

SYSTEM_CHECK_FUNC = load_prompt("check")
SYSTEM_COMMAND_FUNC = load_prompt("command")

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
            trace(GPT_INPUT, message)
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
        trace(GPT_OUTPUT, content)
        cprint(f"Function call result: {function_result}", "cyan")
        return function_result

    trace(GPT_OUTPUT, content)
    cprint(f"GPT Output: {content}", "cyan")
    return content


if not disable_cache:
    gpt_query = memoize(gpt_query)
