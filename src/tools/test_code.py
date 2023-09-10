import pytest
from tools.code import replace_node

ORIGINAL_FUNCTION = """
def greet():
	print("Hello, world!")
"""

NEW_FUNCTION = """
def greet():
	print("Hello, everyone!")
"""


def test_replace_node():
    # Use the replace_node function to replace the original function
    # with the new function
    result = replace_node(ORIGINAL_FUNCTION, "greet", NEW_FUNCTION)

    # Check if NEW_FUNCTION is in the result and ORIGINAL_FUNCTION is not
    assert "Hello, everyone!" in result
    assert "Hello, world!" not in result
