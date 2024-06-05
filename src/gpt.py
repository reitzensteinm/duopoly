import os
from openai import OpenAI
import time
from termcolor import cprint
from tracing.trace import trace
from tracing.tags import GPT_INPUT, GPT_OUTPUT
from utilities.cache import memoize
from utilities.prompts import load_prompt
from settings import get_settings
from tools.code import gpt_query_tools

GPT_3_5 = "gpt-3.5-turbo-1106"
GPT_4 = "gpt-4-1106-preview"
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
    return gpt_query_tools(message, system, functions, model)


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
    """
    Execute a cached GPT query using the given message, system state, functions, and model, requiring a function call if specified.

    Arguments:
    message: A str representing the input message for the GPT model.
    system: A str representing the system state input for the GPT model.
    functions: Optional; A list of dict representing the functions that can be used within the GPT model.
    model: A str representing the model to be used. Defaults to GPT_4.
    require_function: A bool indicating whether a function response is required. Defaults to True.

    Returns:
    str: A string representing the GPT model's output or function call result.
    """
    return gpt_query_tools(message, system, functions, model)
