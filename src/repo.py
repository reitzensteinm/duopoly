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
    repo.git.clean("-f", "-d")


def push_local_branch_to_origin(branch_id: str):
    repo = Repo(os.getcwd())
    repo.git.checkout(branch_id)
    repo.git.push("origin", branch_id, force=True)


def create_pull_request(repo_name: str, branch_id: str, title: str, body: str):
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pr = repo.create_pull(title=title, body=body, head=branch_id, base="main")
    pr.create_review_request(reviewers=["reitzensteinm"])


def find_approved_prs(repo_name: str) -> list[int]:
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    open_pulls = repo.get_pulls(state="open")
    approved_prs_ids = []

    for pr in open_pulls:
        reviews = pr.get_reviews()

        if any(review.state == "APPROVED" for review in reviews):
            approved_prs_ids.append(pr.number)

    return approved_prs_ids


def merge_with_rebase_if_possible(repo_name: str, pr_number: int) -> bool:
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    if pr.mergeable and pr.rebaseable:
        pr.merge(merge_method="rebase")
        close_issue_by_title(repo_name, pr.title)
        return True

    return False


def close_issue_by_title(repo_name: str, issue_title: str) -> None:
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="open")
    for issue in issues:
        if issue.title == issue_title:
            issue.edit(state="closed")
            break


@dataclass
class Issue:
    id: int
    number: int
    title: str
    description: str


def fetch_open_issues(repo_name: str) -> list[Issue]:
    """Fetches open issues from a given repository."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="open")
    issue_data = [
        Issue(
            id=issue.id, number=issue.number, title=issue.title, description=issue.body
        )
        for issue in issues
        if issue.pull_request is None
    ]
    return issue_data


def check_pull_request_title_exists(repo_name: str, pr_title: str) -> bool:
    """Checks if an open pull request with a given title exists."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pull_requests = repo.get_pulls(state="open")
    return any(pr_title == pr.title for pr in pull_requests)


def commit_local_modifications(commit_subject: str, commit_body: str):
    repo = Repo(os.getcwd())
    repo.git.add("--all")
    repo.index.commit(f"{commit_subject}\n\n{commit_body}")


def get_all_checked_in_files():
    repo = Repo(os.getcwd())
    file_list = []
    for obj in repo.tree().traverse():
        if obj.type == "blob":
            file_list.append(obj.path)
    return file_list


def fetch_new_changes():
    repo = Repo(os.getcwd())
    repo.git.fetch()


def is_issue_open(repo_name: str, issue_number: int) -> bool:
    """Checks if a given issue is still open."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(issue_number)
    return issue.state == "open"


def clone_repository(repo_url: str, path: str):
    """Clone the specified repository from GitHub to the specified path."""
    Repo.clone_from(repo_url, path)
