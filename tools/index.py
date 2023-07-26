from src.utilities.minicos import VectorStore


class VectorIndex:
    def __init__(self):
        self.store = VectorStore()

    def ingest(self, source_code):
        pass
