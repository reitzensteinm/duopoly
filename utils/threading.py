import threading
import unittest
import time

_lock = threading.RLock()


def synchronized(func):
    def _synchronized(*args, **kwargs):
        with _lock:
            return func(*args, **kwargs)

    return _synchronized


class TestSynchronized(unittest.TestCase):
    def test_non_reentrant_synchronized(self):
        execution_counter = 0

        @synchronized
        def synchronized_function():
            nonlocal execution_counter
            execution_counter += 1
            time.sleep(1)
            execution_counter -= 1

        t1 = threading.Thread(target=synchronized_function)
        t2 = threading.Thread(target=synchronized_function)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(
            execution_counter, 0, "Synchronized function executed concurrently"
        )

    def test_reentrant_synchronized(self):
        call_counter = 0

        @synchronized
        def reentrant_synchronized_function(level):
            nonlocal call_counter
            call_counter += 1
            if level > 1:
                reentrant_synchronized_function(level - 1)
            call_counter -= 1

        reentrant_synchronized_function(3)
        self.assertEqual(call_counter, 0, "Synchronized reentrant function failed")


if __name__ == "__main__":
    unittest.main()
