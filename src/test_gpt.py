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


def test_gpt_query_tools() -> None:
    """
    Test the gpt_query_tools function with the purpose of being a calculator.
    The test should simulate adding two pairs of numbers together using separate ADD operations,
    and expect two results back simultaneously.

    Assure that two FunctionCalls with expected values are returned from gpt_query_tools.
    The test is currently ignored and should be enabled after the concerned code is implemented.

    Arguments:
    None

    Returns:
    None
    """
    # The test is ignored for now. Uncomment the below code to enable it.
    #
    # add_function = {
    #     "name": "add",
    #     "arguments": {
    #         "x": 1,
    #         "y": 2
    #     }
    # }
    # add_function2 = {
    #     "name": "add",
    #     "arguments": {
    #         "x": 3,
    #         "y": 4
    #     }
    # }
    # system_message = 'This tool is a calculator for adding numbers.'
    # prompt = 'Please add 1 and 2 together. Also, add 3 and 4.'
    # expected_function_calls = [add_function, add_function2]
    # function_calls_returned = gpt_query_tools(prompt, system_message, [ADD])
    #
    # assert function_calls_returned == expected_function_calls, f"Expected function calls to be {expected_function_calls}, but got {function_calls_returned}"
    pass
