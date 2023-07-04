from typing import Dict
import copy


class State:
    def __init__(self, files_dict: Dict[str, str]):
        self.files: Dict[str, str] = copy.deepcopy(files_dict)
        self.original_files: Dict[str, str] = copy.deepcopy(files_dict)
        self.scratch: str = ""
