from git import Repo
from github import Github
import os
from dataclasses import dataclass


def switch_and_reset_branch(branch_id: str):
    repo = Repo(os.getcwd())

    if branch_id not in repo.branches:
        repo.create_head(branch_id)

    repo.git.checkout(branch_id)
    repo.git.reset("--hard", "origin/main")


def push_local_branch_to_origin(branch_id: str):
    repo = Repo(os.getcwd())
    repo.git.checkout(branch_id)


repo.git.push("--force", "origin", branch_id)


def create_pull_request(repo_name: str, branch_id: str, title: str, body: str):
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    repo.create_pull(title=title, body=body, head=branch_id, base="main")


@dataclass
class Issue:
    id: int
    title: str
    description: str


def fetch_open_issues(repo_name: str) -> list[Issue]:
    """Fetches open issues from a given repository."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="open")
    issue_data = [
        Issue(id=issue.id, title=issue.title, description=issue.body)
        for issue in issues
    ]
    return issue_data


def check_pull_request_title_exists(repo_name: str, pr_title: str) -> bool:
    """Checks if an open pull request with a given title exists."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pull_requests = repo.get_pulls(state="open")
    return any(pr_title == pr.title for pr in pull_requests)


def commit_local_modifications():
    repo = Repo(os.getcwd())
    repo.git.add(update=True)
    repo.index.commit("Local modifications committed")
