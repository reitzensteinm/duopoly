import unittest
from tools.hydrate import hydrate_code


class TestHydrate(unittest.TestCase):
    @unittest.skip("Skipping this test")
    def test_functionality(self):
        source_code = """
		def quicksort(arr):
			if len(arr) <= 1:
				return arr
			pivot = arr[len(arr) // 2]
			left = [x for x in arr if x < pivot]
			middle = [x for x in arr if x == pivot]
			right = [x for x in arr if x > pivot]
			return quicksort(left) + middle + quicksort(right)"""

        result = hydrate_code(source_code)

        self.assertIsInstance(result, str)
