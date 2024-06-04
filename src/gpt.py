import os
from openai import OpenAI
import time
from termcolor import cprint
from tracing.trace import trace
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
    functions=None,
    model: str = GPT_4,
    require_function: bool = True,
) -> str:
    """
    Get a response from the GPT model based on the input message and system state.

    Arguments:
    message: A str representing the input message for the GPT model.
    system: A str representing the system state input for the GPT model.
    functions: Optional; A list of dict representing the functions that can be used within the GPT model.
    model: A str representing the model to be used. Defaults to GPT_4.
    require_function: A bool indicating whether a function response is required. Defaults to True.

    Returns:
    str: A string representing the GPT model's output or function call result.
    """
    settings = get_settings()
    if len(message) > settings.max_input_chars:
        raise ValueError("Input exceeds maximum allowed character count")
    if model not in [GPT_4, GPT_3_5]:
        raise ValueError(f"Invalid model specified. Must be '{GPT_4}' or '{GPT_3_5}'.")
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
    message: str, system: str, functions: list, model: str = GPT_4
) -> list:
    """
    This function makes a query to the GPT model with specific system messages and function calls, then returns the function calls made by the model.

    Arguments:
    message: A str representing the user message to be sent to the GPT model.
    system: A str representing the system's part of the conversation.
    functions: A list of functions to be sent to the GPT model.
    model: A str representing the GPT model to be used. Defaults to GPT_4.

    Returns:
    A list of function calls made by the GPT model.
    """
    settings = get_settings()
    tools = [{"type": "function", "function": f} for f in functions]
    if len(message) > settings.max_input_chars:
        raise ValueError("Input exceeds maximum allowed character count")
    if model not in [GPT_4, GPT_3_5]:
        raise ValueError(f"Invalid model specified. Must be '{GPT_4}' or '{GPT_3_5}'.")
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
    function_calls = [call.function for call in tool_calls]
    trace(GPT_OUTPUT, function_calls, (tokens_in, tokens_out))
    cprint(f"Function calls result: {function_calls}", "cyan")
    return function_calls


@memoize
def calculate_text_embedding(text: str) -> list:
    """Calculate text embedding using OpenAI embedding model for the input text.

    Arguments:
    text: A str representing the input text to calculate embeddings for.

    Returns:
    list: A list representing the numerical embedding of the input text.
    """
    embedding_result = client.embeddings.create(
        model="text-embedding-ada-002", input=text
    )
    return list(embedding_result.data[0].embedding)


@memoize
def cached_gpt_query(
    message: str,
    system: str,
    functions=None,
    model: str = GPT_4,
    require_function: bool = True,
) -> str:
    return gpt_query(message, system, functions, model, require_function)
