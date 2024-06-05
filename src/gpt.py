import os
from openai import OpenAI
import time
from termcolor import cprint
from tracing.trace import trace
from typing import Optional, List
from tracing.tags import GPT_INPUT, GPT_OUTPUT
from utilities.cache import memoize
from utilities.prompts import load_prompt
from settings import get_settings

GPT_3_5 = "gpt-3.5-turbo-1106"
GPT_4 = "gpt-4o-2024-05-13"
SYSTEM_CHECK_FUNC = load_prompt("check")
SYSTEM_COMMAND_FUNC = load_prompt("command")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def gpt_query(
    message: str,
    system: str,
    functions: Optional[List[dict]] = None,
    model: str = GPT_4,
    require_function: bool = True,
) -> str:
    """
    Execute a gpt query with specified message, system state, functions, model, and requirement for functions.

    Arguments:
    message: A str representing the input message for the GPT model.
    system: A str representing the system state input.
    functions: Optional; List of dict representing callable functions.
    model: A str representing the chosen GPT model. Defaults to GPT_4.
    require_function: A bool indicating the necessity of function response.

    Returns:
    A str representing the outcome of the GPT model query.
    """
    settings = get_settings()
    if len(message) > settings.max_input_chars:
        raise ValueError("Input exceeds maximum allowed character count")
    if model not in [GPT_4, GPT_3_5]:
        raise ValueError(
            "Invalid model specified. Must be 'gpt-4o-2024-05-13' or 'gpt-3.5-turbo-1106'."
        )
    trace(GPT_INPUT, message)
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
                completion = client.chat.completions.create(
                    model=model, messages=messages, functions=functions
                )
            else:
                completion = client.chat.completions.create(
                    model=model, messages=messages
                )
            function_call = completion.choices[0].message.function_call
            if functions is not None and function_call is None and require_function:
                cprint(
                    f"No functions returned. Message received: {completion.choices[0].message.content}",
                    "red",
                )
                raise Exception("No functions returned")
            end_time = time.time()
            call_duration = end_time - start_time
            tokens_in = completion.usage.prompt_tokens
            tokens_out = completion.usage.completion_tokens
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
    if function_call is not None:
        function_result = function_call
        trace(GPT_OUTPUT, function_result, (tokens_in, tokens_out))
        cprint(f"Function call result: {function_result}", "cyan")
        return function_result
    else:
        content = completion.choices[0].message.content
        trace(GPT_OUTPUT, content, (tokens_in, tokens_out))
        cprint(f"GPT Output: {content}", "cyan")
        return content


def gpt_query_tools(
    message: str, system: str, functions: List[dict], model: str = GPT_4
) -> List[dict]:
    """
    Perform a gpt query with tools and return a list of tool calls made by the model.

    Arguments:
    message: A str with the user's input message.
    system: A str for the system part of the conversation.
    functions: A list of dict for functions included in the query.
    model: A str indicating the GPT model to use.

    Returns:
    A list of dictionaries with the tool calls returned by the model.
    """
    settings = get_settings()
    tools = [{"type": "function", "function": f} for f in functions]
    if len(message) > settings.max_input_chars:
        raise ValueError("Input exceeds maximum allowed character count")
    if model not in [GPT_4, GPT_3_5]:
        raise ValueError(
            "Invalid model specified. Must be 'gpt-4o-2024-05-13' or 'gpt-3.5-turbo-1106'."
        )
    trace(GPT_INPUT, message)
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
            completion = client.chat.completions.create(
                model=model, messages=messages, tools=tools
            )
            tool_calls = completion.choices[0].message.tool_calls
            if tool_calls is None:
                cprint(
                    f"No tool calls returned. Message received: {completion.choices[0].message.content}",
                    "red",
                )
                raise Exception("No tool calls returned")
            end_time = time.time()
            call_duration = end_time - start_time
            tokens_in = completion.usage.prompt_tokens
            tokens_out = completion.usage.completion_tokens
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
    tool_results = [
        {"function": call.function, "result": call.result} for call in tool_calls
    ]
    trace(GPT_OUTPUT, tool_results, (tokens_in, tokens_out))
    cprint(f"Function calls result: {tool_results}", "cyan")
    return tool_results


@memoizem
def calculate_text_embedding(text: str) -> List[float]:
    """
    Calculate text embedding using OpenAI's Ada model for given text.

    Arguments:
    text: A str representing the text to be embedded.

    Returns:
    A list of floats depicting the textual embedding.
    """
    embedding_result = client.embeddings.create(
        model="text-embedding-ada-002", input=text
    )
    return list(embedding_result.data[0].embedding)


@memoize
def cached_gpt_query(
    message: str,
    system: str,
    functions: Optional[List[dict]] = None,
    model: str = GPT_4,
    require_function: bool = True,
) -> str:
    """
    Cache a gpt query to avoid duplicate computation on repeated calls with identical arguments.

    Arguments:
    message: A str for the message input.
    system: A str for the system state.
    functions: Optional; dictates functions that are passed to the query.
    model: A str for the selected GPT model.
    require_function: A bool for whether the function's response is required.

    Returns:
    A str with the result of the cached GPT query.
    """
    return gpt_query(message, system, functions, model, require_function)
