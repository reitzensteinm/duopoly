import re
from git import Repo
from github import Github
import os
import pathspec
from dataclasses import dataclass
import time
import subprocess


def switch_and_reset_branch(branch_id: str, target_dir: str = os.getcwd()):
    repo = Repo(target_dir)

    if branch_id not in repo.branches:
        repo.create_head(branch_id)

    repo.git.checkout(branch_id)
    repo.git.reset("--hard", "origin/main")
    repo.git.clean("-f", "-d")


def push_local_branch_to_origin(branch_id: str, target_dir: str = os.getcwd()):
    repo = Repo(target_dir)
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
    branch = pr.head

    if pr.mergeable and pr.rebaseable:
        pr.merge(merge_method="rebase")
        close_issue_by_title(repo_name, pr.title)
        delete_branch_after_merge(g, repo_name, branch)
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


def delete_branch_after_merge(g, repo_name, branch):
    retries = 5
    while retries > 0:
        try:
            g.get_repo(repo_name).get_git_ref(f"heads/{branch.ref}").delete()
            break
        except Exception as e:
            print(e)
            retries -= 1
            time.sleep(2)  # Wait before retrying


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


def commit_local_modifications(
    commit_subject: str, commit_body: str, target_dir: str = os.getcwd()
):
    repo = Repo(target_dir)
    repo.git.add("--all")
    repo.index.commit(f"{commit_subject}\n\n{commit_body}")


def get_all_checked_in_files(target_dir: str = os.getcwd()):
    repo = Repo(target_dir)
    file_list = []
    for obj in repo.tree().traverse():
        if obj.type == "blob":
            file_list.append(obj.path)
    return file_list


def fetch_new_changes(target_dir: str = os.getcwd()):
    repo = Repo(target_dir)
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


def check_issue_has_open_pr_with_same_title(repo_name: str, issue_title: str) -> bool:
    """Checks if an issue has an open PR with the same title."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pull_requests = repo.get_pulls(state="open")
    return any(issue_title == pr.title for pr in pull_requests)


def get_issue_dependencies(repo_name: str, issue_number: int) -> list[int]:
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(issue_number)
    issue_body = issue.body
    pattern = r"#\d+"
    matches = re.findall(pattern, issue_body)
    dependencies = [int(match.replace("#", "")) for match in matches]
    return dependencies


def check_dependency_issues(repo_name: str, issue_number: int) -> bool:
    """Check if an issue has any open dependencies."""
    dependencies = get_issue_dependencies(repo_name, issue_number)
    for dep in dependencies:
        if is_issue_open(repo_name, dep):
            return True
    return False


def git_reset(directory: str):
    try:
        subprocess.check_call(["git", "reset", "--hard"], cwd=directory)
    except subprocess.CalledProcessError as e:
        raise Exception("git reset failed") from e


def find_git_repo(directory: str) -> str:
    while directory != os.path.dirname(directory):  # While the directory has a parent
        try:
            Repo(directory)  # Try to create a Repo object
            return directory  # If successful, return the directory
        except Exception:
            pass
        directory = os.path.dirname(directory)  # Go up one directory level
    return None


def list_files(target_directory, gitignore_path):
    """Lists all the files in a directory that aren't excluded by a gitignore file."""
    with open(gitignore_path, "r") as f:
        lines = f.readlines()
    spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
    matches = []
    for root, dirs, files in os.walk(target_directory):
        for fname in files:
            if not spec.match_file(os.path.join(root, fname)):
                matches.append(os.path.join(root, fname))
    return matches
