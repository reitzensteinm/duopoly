"""
This file 'test_gpt.py' provides a JSON schema for a test 'add' function that adds two integers together.
It is used to demonstrate and validate the structure of test function schemas within this project.
"""
ADD: dict = {
    "name": "add",
    "description": "Adds two integers together and returns the sum.",
    "parameters": {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "The first integer to add."},
            "y": {"type": "integer", "description": "The second integer to add."},
        },
        "required": ["x", "y"],
    },
    "returns": {"type": "integer", "description": "The sum of the two input integers."},
}
