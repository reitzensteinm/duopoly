from typing import Dict, List
import copy
from utils import replace_spaces_with_tabs, annotate_with_line_numbers


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
        Renders information including files as a string with a FILES header, filenames, and
        processed contents with replace_spaces_with_tabs and annotate_with_line_numbers from utils.py.

        Returns:
            str: The formatted string containing keys with values and annotated file contents.
        """
        rendered_info = ["### FILES ###"]
        for filename in self.context_files:
            contents = self.files.get(filename, "")
            processed_contents = replace_spaces_with_tabs(contents)
            processed_contents = annotate_with_line_numbers(processed_contents)
            file_header = f"*** {filename} ***"
            rendered_info.append(f"{file_header}\n{processed_contents}")

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
