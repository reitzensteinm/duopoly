from typing import Dict, List
import copy


class State:
    def __init__(self, files_dict: Dict[str, str], target_dir: str = None):
        self.files: Dict[str, str] = copy.deepcopy(files_dict)
        self.original_files: Dict[str, str] = copy.deepcopy(files_dict)
        self.scratch: str = ""
        self.target_dir: str = target_dir
        self.last_command = None
        self.information: Dict[str, str] = {}
        self.context_files: List[str] = []

    def render_information(self) -> str:
        """
        Renders information as a string where every key is surrounded by '***' and displayed above its value.

        Returns:
                str: The formatted string containing keys and values.
        """
        rendered_info = []
        for key, value in self.information.items():
            rendered_info.append(f"*** {key} ***\n{value}")
        return "\n\n".join(rendered_info)

    def add_file(self, filename: str) -> None:
        """
        Adds a filename to the context_files list, ignoring duplicates.

        Arguments:
                filename (str): The filename to add.

        Returns:
                None
        """
        if filename not in self.context_files:
            self.context_files.append(filename)
