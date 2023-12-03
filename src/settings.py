import yaml
import threading
from typing import Optional, Any, List

PARSED_ARGS: Optional[Any] = None
"""A dictionary of the parsed command line arguments.

This constant is intended to be set in main.py with the actual parsed arguments from the command line after argparse processing. It is initialized as None and should be of type Optional[dict] to allow for type checking and to indicate that it may not yet be set at the time of module import.
"""
_thread_local_settings = threading.local()


class Settings:
    check_open_pr: bool = True
    """Indicates whether to check for open pull requests, defaulting to True.

    This class property of type bool determines if open pull requests should be checked for, with a default value set to True.
    """

    def __init__(self) -> None:
        """Initialize the Settings with default configuration values including reviewers, workers, input chars, tools, quality checks, and issue retries.

        This constructor sets up the Settings object with default values such as an empty list of reviewers (list),
        a maximum number of workers (int), maximum input characters (int), flags for use of tools (bool), and quality checks (bool),
        and a maximum number of issue retries (int, defaulting to 2).
        Command line arguments can override these settings by call to apply_commandline_overrides at the end.
        """
        self.reviewers: List[str] = []
        self.max_workers: int = 10
        self.max_input_chars: int = 48000
        self.use_tools: bool = False
        self.quality_checks: bool = True
        self.max_issue_retries: int = 2
        self.max_loop_length: int = 15
        self.apply_commandline_overrides()


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
PYLINT_RETRIES = 0
CHECK_OPEN_PR = True
settings = Settings()
