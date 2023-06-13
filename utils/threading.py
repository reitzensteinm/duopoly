import threading

_lock = threading.RLock()


def synchronized(func):
    def _synchronized(*args, **kwargs):
        with _lock:
            return func(*args, **kwargs)

    return _synchronized
