class Settings:
    def __init__(self):
        self.reviewers = []


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
