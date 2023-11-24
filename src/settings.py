import yaml
import threading

_thread_local_settings = threading.local()


class Settings:
    def __init__(self):
        self.max_workers: int = 10  # Maximum number of workers for concurrency
        self.reviewers: list = []  # List of reviewers for the settings

    def load_from_yaml(self, filepath: str = "duopoly.yaml") -> None:
        """
        Load settings from a YAML file.

        This method updates the object's attributes from a given YAML file.

        Arguments:
                filepath: A string representing the path to the YAML file.

        Returns:
                None
        """
        with open(filepath, "r") as yamlfile:
            data = yaml.safe_load(yamlfile)

        if "reviewers" in data:
            self.reviewers = data["reviewers"]


def get_settings() -> Settings:
    """
    Retrieve the instance of the Settings class for the current thread.

    If the settings instance does not exist, it will return a new one.

    Arguments:
            None.

    Return value:
            The Settings instance.
    """
    if hasattr(_thread_local_settings, "settings"):
        return _thread_local_settings.settings
    return settings


def apply_settings(yaml_path: str) -> None:
    """
    Apply the settings from the specified YAML file.

    Arguments:
            yaml_path: A string representing the path to the YAML configuration file.

    Return value:
            None.
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
REQUEST_REVIEW_FOR_PRS = True
PR_REVIEWER_USERNAME = "reitzensteinm"
MAX_INPUT_CHARS = 48000
PYLINT_RETRIES = 1
CHECK_OPEN_PR = False
settings = Settings()
