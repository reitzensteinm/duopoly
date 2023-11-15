from typing import Dict
import copy


class State:
    def __init__(self, files_dict: Dict[str, str], target_dir: str = None):
        self.files: Dict[str, str] = copy.deepcopy(files_dict)
        self.original_files: Dict[str, str] = copy.deepcopy(files_dict)
        self.scratch: str = ""
        self.target_dir: str = target_dir
        self.last_command = None
        self.information: Dict[str, str] = {}

    def render_information(self) -> str:
        rendered_info = []
        for key, value in self.information.items():
            rendered_info.append(f"{key}:\n{value}")
        return "\n\n".join(rendered_info)
