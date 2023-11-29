import yaml
import threading
from typing import Optional, Any, List

PARSED_ARGS: Optional[Any] = None
"""A dictionary of the parsed command line arguments.

This constant is intended to be set in main.py with the actual parsed arguments from the command line after argparse processing. It is initialized as None and should be of type Optional[dict] to allow for type checking and to indicate that it may not yet be set at the time of module import.
"""
_thread_local_settings = threading.local()

MAX_LOOP_LENGTH: int = 15
"""The maximum length allowed for loops in the program's settings context.

This constant represents the upper limit on the number of iterations a loop within the application is allowed to execute.
"""


class Settings:
    def __init__(self) -> None:
        """Initialize the Settings with default configuration values including reviewers, workers, input chars, tools, quality checks, issue retries, and max loop length.

        This constructor sets up the Settings object with default values such as an empty list of reviewers (list),
        a maximum number of workers (int), maximum input characters (int), flags for use of tools (bool), quality checks (bool),
        a maximum number of issue retries (int, defaulting to 2), and maximum loop length (int, defaulting to MAX_LOOP_LENGTH).
        Command line arguments can override these settings by call to apply_commandline_overrides at the end.
        """
        self.reviewers: List[str] = []
        self.max_workers: int = 10
        self.max_input_chars: int = 48000
        self.use_tools: bool = False
        self.quality_checks: bool = True
        self.max_issue_retries: int = 2
        self.max_loop_length: int = MAX_LOOP_LENGTH
        self.apply_commandline_overrides()

    def load_from_yaml(self, filepath: str = "duopoly.yaml") -> None:
        """Load settings from a YAML file and apply command line overrides.

        Args:
            filepath (str): The path to the YAML settings file to load.

        This method updates the instance with settings from the YAML file at `filepath` and applies overrides.
        """
        with open(filepath, "r") as yamlfile:
            data = yaml.safe_load(yamlfile)
        if "reviewers" in data:
            self.reviewers = data["reviewers"]
        if "quality_checks" in data and data["quality_checks"] is not None:
            self.quality_checks = data["quality_checks"]
        self.apply_commandline_overrides()

    def apply_commandline_overrides(self) -> None:
        """Override settings based on parsed command line arguments.

        Utilizes the global PARSED_ARGS to set settings for quality checks and use of tools, if specified.
        """
        global PARSED_ARGS
        if PARSED_ARGS:
            if (
                "quality_checks" in PARSED_ARGS
                and PARSED_ARGS["quality_checks"] is not None
            ):
                self.quality_checks = PARSED_ARGS.get(
                    "quality_checks", self.quality_checks
                )
            self.use_tools = PARSED_ARGS.get("use_tools", self.use_tools)


def get_settings() -> Settings:
    """Retrieve the current thread-local Settings instance or the global instance if not set.

    Returns:
        Settings: The current thread-local Settings instance or the global Settings instance.

    This function fetches the Settings object associated with the thread-local storage.
    If it does not exist, it returns the global Settings instance.
    """
    if hasattr(_thread_local_settings, "settings"):
        return _thread_local_settings.settings
    return settings


def apply_settings(yaml_path: str) -> None:
    """Create a new Settings instance from a YAML file and store it in thread-local storage.

    Args:
        yaml_path (str): The path to the YAML file from which to load settings.

    This function creates a new Settings instance, loads settings from the specified YAML file,
    and stores it in the thread-local storage.
    """
    instance = Settings()
    instance.load_from_yaml(yaml_path)
    _thread_local_settings.settings = instance


REPOSITORY_PATH = ["reitzensteinm/duopoly", "reitzensteinm/duopoly-website"]
CODE_PATH = "src"
GITIGNORE_PATH = ".gitignore"
ADMIN_USERS = ["reitzensteinm", "Zylatis", "atroche"]
PYLINT_RETRIES = 1
CHECK_OPEN_PR = True
settings = Settings()
