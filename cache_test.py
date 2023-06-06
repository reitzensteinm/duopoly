import pytest
from datetime import datetime
from cache import memoize


def test_memoize_side_effects():
    side_effect_value = []

    @memoize
    def side_effect_function(arg1, arg2):
        side_effect_value.append(arg1)
        return arg1 + arg2

    test_arg1 = datetime.now().timestamp()
    test_arg2 = 5

    result1 = side_effect_function(test_arg1, test_arg2)
    result2 = side_effect_function(test_arg1, test_arg2)

    assert len(side_effect_value) == 1
    assert result1 == result2
