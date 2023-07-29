import os
import hashlib
import json


class KeyValueStore:
    def __init__(self):
        self.cache_dir = ".cache/"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def read(self, key):
        key_hash = self._hash_key(key)
        file_path = self.cache_dir + key_hash
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Key not found: {key}")

        with open(file_path, "r") as file:
            value = json.load(file)
        return value

    def write(self, key, value):
        key_hash = self._hash_key(key)
        file_path = self.cache_dir + key_hash

        with open(file_path, "w") as file:
            json.dump(value, file)

    def _hash_key(self, key):
        md5_hash = hashlib.md5()
        md5_hash.update(key.encode("utf-8"))
        hashed_key = md5_hash.hexdigest()
        return hashed_key


def memoize(func):
    kv_store = KeyValueStore()

    def memoized_func(*args, **kwargs):
        key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
        try:
            return kv_store.read(key)
        except FileNotFoundError:
            result = func(*args, **kwargs)
            kv_store.write(key, result)
            return result

    return memoized_func


def read(key):
    store = KeyValueStore()
    return store.read(key)


def write(key, value):
    store = KeyValueStore()
    store.write(key, value)
