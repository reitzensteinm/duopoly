import yaml
import threading

_thread_local_settings = threading.local()


class Settings:
    def __init__(self):
        self.reviewers = []

    def load_from_yaml(self, filepath="duopoly.yaml"):
        with open(filepath, "r") as yamlfile:
            data = yaml.safe_load(yamlfile)

        if "reviewers" in data:
            self.reviewers = data["reviewers"]


def get_settings():
    if hasattr(_thread_local_settings, "settings"):
        return _thread_local_settings.settings
    return settings


def apply_settings(yaml_path):
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
PYLINT_RETRIES = 0
CHECK_OPEN_PR = False

settings = Settings()
