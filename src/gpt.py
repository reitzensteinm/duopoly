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
GPT_4 = "gpt-4-1106-preview"
SYSTEM_CHECK_FUNC = load_prompt("check")
SYSTEM_COMMAND_FUNC = load_prompt("command")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def gpt_query_tools(
    message: str, system: str, functions: list, model: str = GPT_4
) -> list:
    """
    This function makes a query to the GPT model with specific system messages and function calls, then returns the function calls made by the model.

    Arguments:
    message: A str representing the user message to be sent to the GPT model.
    system: A str representing the system's part of the conversation.
    functions: A list of functions to be sent to the GPT model.
    model: A str representing the GPT model to be used. Defaults to 'gpt-4'.

    Returns:
    A list of function calls made by the GPT model.
    """
    settings = get_settings()
    tools = [{"type": "function", "function": f} for f in functions]
    if len(message) > settings.max_input_chars:
        raise ValueError("Input exceeds maximum allowed character count")
    if model not in [GPT_4, GPT_3_5]:
        raise ValueError("Invalid model specified. Must be 'gpt-4' or 'gpt-3.5-turbo'.")
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
    functions: list,
    model: str = GPT_4,
    require_function: bool = True,
) -> list:
    """
    Retrieve a list of function calls made by the GPT model based on the input message, system state, and available functions.

    Arguments:
    message: A str representing the user's input message to the GPT model.
    system: A str representing the system state information for the conversation.
    functions: A list of dict representing available functions to be used by the GPT model.
    model: A str representing the GPT model to be used. Defaults to GPT_4.
    require_function: A bool indicating whether a function call response is required. Defaults to True.

    Returns:
    list: A list of function calls made by the GPT model, if any.
    """
    return gpt_query_tools(message, system, functions, model)
