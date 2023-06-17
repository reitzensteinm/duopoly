import os
import pytest

from pipeline.issue import apply_prompt_to_files


@pytest.fixture
def input_file():
    empty_file = ""
    return empty_file


def test_apply_prompt_to_files(input_file):
    prompt = "create a function called add_test which adds one to the input"
    result_files = apply_prompt_to_files(prompt, {"test_file.py": input_file})
    test_file = result_files["test_file.py"]
    exec_globals = {}
    exec(test_file, exec_globals)
    add_test = exec_globals["add_test"]
    assert add_test(3) == 4
    assert add_test(-5) == -4
    assert add_test(0) == 1
