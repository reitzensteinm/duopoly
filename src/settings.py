import yaml
import threading
from typing import Optional, Any, List

PARSED_ARGS: Optional[Any] = None
"""A dictionary of the parsed command line arguments.

This constant is intended to be set in main.py with the actual parsed arguments from the command line after argparse processing. It is initialized as None and should be of type Optional[dict] to allow for type checking and to indicate that it may not yet be set at the pattern of module import.
"""
_thread_local_settings = threading.local()


class Settings:
    def __init__(self) -> None:
        """Initialize the Settings with default configuration values including reviewers, workers, input chars, use of tools by default, quality checks, issue retries, and check for open PRs.

        This constructor sets up the Settings object with default values such as an empty list of reviewers (list),
        a maximum number of workers (int), maximum input characters (int), flags for use of tools (bool), quality checks (bool),
        a maximum number of issue retries (int, defaulting to 2), and a boolean to check for open PRs (bool), defaulting to True.
        Use of tools is now enabled by default (bool, defaulting to True). Command line arguments can override these settings by call to apply_commandline_overrides at the end.
        """
        self.reviewers: List[str] = []
        self.max_workers: int = 10
        self.max_input_chars: int = 48000
        self.use_tools: bool = True
        self.quality_checks: bool = True
        self.max_issue_retries: int = 2
        self.max_loop_length: int = 15
        self.check_open_pr: bool = True
        """A boolean indicating if the system should check for open pull requests.

        The default value is set to True to enable checking of open pull requests by default.
		"""
        self.apply_commandline_overrides()

    def load_from_yaml(self, filepath: str = "duopoly.yaml") -> None:
        """Load settings from a 'settings' subsection of a YAML file and apply command line overrides.

        Args:
                filepath (str): The path to the YAML settings file to load.

        This method updates the instance with settings from the 'settings' subsection of the YAML file at `filepath` and applies overrides.
        """
        with open(filepath, "r") as yamlfile:
            data = yaml.safe_load(yamlfile)
        if "settings" in data:
            settings_data = data["settings"]
            if "reviewers" in settings_data:
                self.reviewers = settings_data["reviewers"]
            if (
                "quality_checks" in settings_data
                and settings_data["quality_checks"] is not None
            ):
                self.quality_checks = settings…
