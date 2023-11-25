import yaml
import threading
from typing import Optional, Any

_thread_local_settings = threading.local()


class Settings:
    def __init__(self):
        """Initialize the Settings with the default configuration values."""
        self.reviewers = []
        self.max_workers = 10
        self.MAX_INPUT_CHARS = 48000
        self.use_tools: bool = False
        self.do_quality_checks: bool = True

    def load_from_yaml(self, filepath: str = "duopoly.yaml") -> None:
        """Load settings from the specified YAML file.

        Args:
                        filepath (str): The path to the YAML settings file to load.
        """
        with open(filepath, "r") as yamlfile:
            data = yaml.safe_load(yamlfile)
        if "reviewers" in data:
            self.reviewers = data["reviewers"]

    def apply_commandline_overrides(self, do_quality_checks: bool) -> None:
        """Override class variables based on command line arguments.

        Args:
                        do_quality_checks (bool): Indicate whether to perform quality checks.
        """
        self.do_quality_checks = do_quality_checks


def get_settings() -> Settings:
    """Retrieve the current settings instance.

    Returns:
            Settings: The current thread-local Settings instance.

    This function fetches the Settings object associated with the thread-local
    storage. If it does not exist, it returns the global Settings instance.
    """
    if hasattr(_thread_local_settings, "settings"):
        return _thread_local_settings.settings
    return settings


def apply_settings(yaml_path: str) -> None:
    """Apply settings from a YAML file to the current Settings instance.

    Args:
            yaml_path (str): The path to the YAML file from which to load settings.

    This function creates a new Settings instance, loads settings from the
    specified YAML file, and stores it in the thread-local storage.
    """
    instance = Settings()
    instance.load_from_yaml(yaml_path)
    _thread_local_settings.settings = instance


REPOSITORY_PATH = ["reitzensteinm/duopoly", "reitzensteinm/duopoly-website"]
CODE_PATH = "src"
GITIGNORE_PATH = ".gitignore"
ADMIN_USERS = ["reitzensteinm", "Zylatis", "atroche"]
TOKEN_LIMIT = 40000
DO_QUALITY_CHECKS = True
PYLINT_RETRIES = 1
CHECK_OPEN_PR = False
settings = Settings()
PARSED_ARGS: Optional[Any] = None
"""A dictionary of the parsed command line arguments.

This constant is intended to be set in main.py with the actual parsed arguments
from the command line after argparse processing. It is initialized as None and
should be of type Optional[dict] to allow for type checking and to indicate that
it may not yet be set at the time of module import.
"""
