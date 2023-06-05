import pytest
from utils import partition_by_predicate


import pytest
from utils import partition_by_predicate


@pytest.mark.parametrize(
    "input_list, expected",
    [
        (
            [1, 2, 3, 4, 5, 6, 8, 10],
            [[1], [2, 3], [4, 5], [6], [8], [10]],
        ),
        (
            [],
            [],
        ),
        (
            [1, 3, 5, 7, 9],
            [[1, 3, 5, 7, 9]],
        ),
        (
            [2, 4, 6, 8, 10],
            [[2], [4], [6], [8], [10]],
        ),
    ],
)
def test_partition_by_predicate(
    input_list,
    expected,
):
    assert partition_by_predicate(input_list, lambda x: x % 2 == 0) == expected
