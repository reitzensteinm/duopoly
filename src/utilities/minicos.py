from typing import List
import numpy as np


def cosine_similarity(vec1, vec2):
    vec1_norm = np.linalg.norm(vec1)
    vec2_norm = np.linalg.norm(vec2)
    return np.dot(vec1, vec2) / (vec1_norm * vec2_norm)


class Entry:
    def __init__(self, key: np.ndarray, value: str):
        self.key = key
        self.value = value


class VectorStore:
    def __init__(self):
        self.entries = []

    def add_entry(self, key: np.ndarray, value: str):
        self.entries.append(Entry(key, value))

    def search(self, vec: np.ndarray, n: int) -> List[str]:
        # Calculate similarities and track top n
        similarities = [
            (entry.value, cosine_similarity(vec, entry.key)) for entry in self.entries
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [similarity[0] for similarity in similarities[:n]]
