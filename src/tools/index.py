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

    def retrieve(self, search_text, num_items):
        embedding = calculate_text_embedding(search_text)
        embedding = np.array(embedding)
        entries = self.store.search(embedding, num_items)
        return entries
