import pytest
from tools.code import replace_node

ORIGINAL_CODE = """
def greet():
	print("Hello, world!")
CONSTANT = 'old_value'
"""

NEW_CODE = """
def greet():
	print("Hello, everyone!")
"""

NEW_CONSTANT = "CONSTANT = 'new_value'"


def test_replace_node():
    # Use the replace_node function to replace the original function
    # with the new function
    result = replace_node(ORIGINAL_CODE, "greet", NEW_CODE)

    # Check if NEW_FUNCTION is in the result and ORIGINAL_FUNCTION is not
    assert "Hello, everyone!" in result
    assert "Hello, world!" not in result


def test_replace_constant():
    # Use the replace_node function to replace the CONSTANT
    # with the NEW_CONSTANT
    result = replace_node(ORIGINAL_CODE, "CONSTANT", NEW_CONSTANT)

    # Check if NEW_CONSTANT is in the result and CONSTANT is not
    assert "CONSTANT = 'new_value'" in result
    assert "CONSTANT = 'old_value'" not in result
