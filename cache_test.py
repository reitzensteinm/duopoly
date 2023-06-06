import time
from cache import memoize


def test_memoize_function_cache():
    @memoize
    def memoized_function(timestamp):
        return timestamp

    start_time = time.time()

    first_call = memoized_function(start_time)
    second_call = memoized_function(start_time)

    assert (
        first_call == second_call
    ), "Memoization is not caching the function call properly."

    different_call = memoized_function(time.time())

    assert (
        first_call != different_call
    ), "Memoization should not cache when different arguments are provided."
