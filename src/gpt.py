import os
import openai
import time
from utils import read_file, write_file, partition_by_predicate
from termcolor import cprint
from tracing.trace import trace
from tracing.tags import GPT_INPUT, GPT_OUTPUT
from utilities.cache import memoize
from utilities.prompts import load_prompt
from settings import MAX_INPUT_CHARS

GPT_3_5 = "gpt-3.5-turbo-1106"
GPT_4 = "gpt-4-1106-preview"
SYSTEM_CHECK_FUNC = load_prompt("check")
SYSTEM_COMMAND_FUNC = load_prompt("command")


def gpt_query(
    message: str,
    system: str,
    functions=None,
    model: str = GPT_4,
    require_function: bool = True,
) -> str:
    if len(message) > MAX_INPUT_CHARS:
        raise ValueError("Input exceeds maximum allowed character count")
    if model not in [GPT_4, GPT_3_5]:
        raise ValueError("Invalid model specified. Must be 'gpt-4' or 'gpt-3.5-turbo'.")
    openai.api_key = os.environ["OPENAI_API_KEY"]
    retries = 2
    backoff = 1
    for i in range(retries):
        try:
            start_time = time.time()
            cprint(f"GPT Input: {message}", "blue")
            messages = [
                {"role": "system", "content": system},
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
    trace(GPT_INPUT, message, (tokens_in, tokens_out))
    if "function_call" in completion.choices[0].message:
        function_result = completion.choices[0].message["function_call"]
        trace(GPT_OUTPUT, function_result, (tokens_in, tokens_out))
        cprint(f"Function call result: {function_result}", "cyan")
        return function_result
    else:
        content = completion.choices[0].message.content
        trace(GPT_OUTPUT, content, (tokens_in, tokens_out))
        cprint(f"GPT Output: {content}", "cyan")
        return content


@memoize
def calculate_text_embedding(text: str):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    embedding_result = openai.Embedding.create(
        model="text-embedding-ada-002", input=text
    )
    return list(embedding_result["data"][0]["embedding"])


@memoize
def cached_gpt_query(
    message: str,
    system: str,
    functions=None,
    model: str = GPT_4,
    require_function: bool = True,
) -> str:
    return gpt_query(message, system, functions, model, require_function)
