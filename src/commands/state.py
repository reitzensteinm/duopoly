from typing import Dict


class State:
    def __init__(self, files_dict: Dict[str, str]):
        self.files: Dict[str, str] = dict(files_dict)
        self.original_files: Dict[str, str] = dict(files_dict)
        self.scratch: str = ""
