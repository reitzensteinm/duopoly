import pytest
from utils import partition_by_predicate


def test_partition_by_predicate_even():
    assert partition_by_predicate([1, 2, 3, 4, 5, 6, 8, 10], lambda x: x % 2 == 0) == [
        [1],
        [2, 3],
        [4, 5],
        [6],
        [8],
        [10],
    ]


def test_partition_by_predicate_empty_list():
    assert partition_by_predicate([], lambda x: x % 2 == 0) == []


def test_partition_by_predicate_no_true_predicate():
    assert partition_by_predicate([1, 3, 5, 7, 9], lambda x: x % 2 == 0) == [
        [1, 3, 5, 7, 9]
    ]


def test_partition_by_predicate_all_true_predicate():
    assert partition_by_predicate([2, 4, 6, 8, 10], lambda x: x % 2 == 0) == [
        [2],
        [4],
        [6],
        [8],
        [10],
    ]


def test_partition_by_predicate_single_element():
    assert partition_by_predicate([3], lambda x: x % 2 == 0) == [[3]]
