from utilities.minicos import VectorStore
from gpt import calculate_text_embedding
import numpy as np


class VectorIndex:
    def __init__(self):
        self.store = VectorStore()

    def ingest(self, source_code):
        embedding = calculate_text_embedding(source_code)
        embedding = np.array(embedding)
        self.store.add_entry(embedding, source_code)
