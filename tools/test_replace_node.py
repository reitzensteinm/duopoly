import pytest
from .replace_node import replace_node


def test_replace_node():
    # Basic function replacement
    original_code = """
	def hello():
		print('Hello, World!')
	"""
    replacement_code = """
	def hello():
		print('Hello, Universe!')
	"""

    modified_code = replace_node(original_code, "hello", replacement_code)
    expected_result = """
	def hello():
		print('Hello, Universe!')
	"""

    assert modified_code == expected_result

    # Class method replacement
    original_code = """
	class TestClass:
		def test_method(self):
			return "Hello, World!"
	"""
    replacement_code = """
	def test_method(self):
		return "Hello, Universe!"
	"""

    modified_code = replace_node(original_code, "test_method", replacement_code)
    expected_result = """
	class TestClass:
		def test_method(self):
			return "Hello, Universe!"
	"""

    assert modified_code == expected_result

    # Test when node does not exist
    with pytest.raises(ValueError):
        replace_node(original_code, "non_existing_method", replacement_code)
