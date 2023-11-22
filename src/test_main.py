import os
import pytest
from pipeline.issue import apply_prompt_to_files
from tracing.trace import create_trace, bind_trace, trace


@pytest.fixture
def input_file():
    empty_file = ""
    return empty_file


def test_apply_prompt_to_files(input_file):
    """
    Tests the 'apply_prompt_to_files' function by creating files based on prompts.

    This test initializes a prompt for file creation, applies the prompt to generate new file contents,
    and asserts correctness of the created function.

    Args:
    input_file: A fixture providing an empty file.

    Returns:
    None
    """
    trace_instance = create_trace("test_apply_prompt_to_files")
    bind_trace(trace_instance)
    try:
        prompt = "create a function called add_test which adds one to the input"
        result_files = apply_prompt_to_files(prompt, {"src/test_file.py": input_file})
        test_file = result_files["src/test_file.py"]
        exec_globals = {}
        exec(test_file, exec_globals)
        add_test = exec_globals["add_test"]
        assert add_test(3) == 4
        assert add_test(-5) == -4
        assert add_test(0) == 1
    except Exception as e:
        trace("EXCEPTION", str(e))
        raise
