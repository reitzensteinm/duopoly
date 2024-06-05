import yaml
import threading
from typing import Optional, Any, List

PARSED_ARGS: Optional[Any] = None
"""A dictionary of the parsed command line arguments.

This constant is intended to be set in main.py with the actual parsed arguments from the command line after argparse processing. It is initialized as None and should be of type Optional[dict] to allow for type checking and to indicate that it may not yet be set at the time of module import.
"""
_thread_local_settings = threading.local()


class Settings:

    def __init__(self) -> None:
        """Initialize the Settings with default configuration values.

        Default values include an empty list of reviewers, a maximum of 10 workers, 48000 input characters, use tools set to True, enable quality checks,
        2 issue retries, maximum loop length of 15, and automatic check for open PRs at startup.
        """
        self.reviewers: List[str] = []
        self.max_workers: int = 10
        self.max_input_chars: int = 48000
        self.use_tools: bool = True
        self.quality_checks: bool = True
        self.max_issue_retries: int = 2
        self.max_loop_length: int = 15
        self.check_open_pr: bool = True
        self.apply_commandline_overrides()


def get_settings() -> Settings:
    """Retrieve the current thread-local Settings instance or the global instance if not set.

    This function fetches the Settings object associated with the thread-local storage, or returns the global Settings instance if not set.
    """
    if hasattr(_thread_local_settings, "settings"):
        return _thread_local_settings.settings
    return settings


def apply_settings(yaml_path: str) -> None:
    """Create a new Settings instance from a YAML file and store it in thread-local storage.

    It creates a new Settings instance, loads settings from the specified YAML file, and stores it in the thread-local storage.
    """
    instance = Settings()
    instance.load_from_yaml(yaml_path)
    _thread_open_settings.settings = instance


REPOSITORY_PATH = ["reitzensteinm/duopoly", "reitzensteinm/duopoly-website"]
CODE_PATH = "src"
GITIGNORE_PATH = ".gitignore"
ADMIN_USERS = ["reitzensteinm", "Zylatis", "atroche"]
PYLINT_RETRIES = 0
settings = Settings()
