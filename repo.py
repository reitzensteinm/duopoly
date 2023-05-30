from git import Repo
from github import Github
import os


def switch_and_reset_branch(branch_id: str):
    repo = Repo(os.getcwd())

    if branch_id not in repo.branches:
        repo.create_head(branch_id)

    repo.git.checkout(branch_id)
    repo.git.pull("origin", branch_id)
    repo.git.reset("--hard", "origin/main")


def push_local_branch_to_origin(branch_id: str):
    repo = Repo(os.getcwd())
    repo.git.checkout(branch_id)
    repo.git.push("origin", branch_id)


def create_pull_request(repo_name: str, branch_id: str, title: str, body: str):
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    repo.create_pull(title=title, body=body, head=branch_id, base="main")


def fetch_open_issues(repo_name: str) -> list[str]:
    """Fetches open issues from a given repository."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="open")
    descriptions = [issue.body for issue in issues]
    return descriptions


def commit_local_modifications():
    repo = Repo(os.getcwd())
    repo.git.add(update=True)
    repo.index.commit("Local modifications committed")
