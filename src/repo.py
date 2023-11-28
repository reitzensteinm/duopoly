import re
import shutil
from git import Repo
from github import Github
import os
import pathspec
from dataclasses import dataclass
import time
import subprocess
from pathlib import Path
from typing import List, Optional


@dataclass
class IssueComment:
    """Represents a comment on a GitHub issue."""

    username: str
    content: str


@dataclass
class Issue:
    """Represents a GitHub issue with related metadata."""

    id: int
    number: int
    title: str
    description: str
    repository: str
    comments: List[IssueComment]
    author: str


def switch_and_reset_branch(branch_id: str, target_dir: str = os.getcwd()) -> None:
    """Switch to a specified branch and reset it to match the origin/main branch."""
    repo = Repo(target_dir)
    if branch_id not in repo.branches:
        repo.create_head(branch_id)
    repo.git.checkout(branch_id)
    repo.git.reset("--hard", "origin/main")
    repo.git.clean("-f", "-d")


def push_local_branch_to_origin(branch_id: str, target_dir: str = os.getcwd()) -> None:
    """Pushes a local branch to the remote repository, forcibly overwriting it."""
    repo = Repo(target_dir)
    repo.git.checkout(branch_id)
    repo.git.push("origin", branch_id, force=True)


def create_pull_request(repo_name: str, branch_id: str, title: str, body: str) -> None:
    """Creates a pull request on GitHub with the specified details and requests reviews based on settings.

    Args:
        repo_name (str): The name of the target repository.
        branch_id (str): The id of the branch for which the pull request is created.
        title (str): The title of the pull request.
        body (str): The body description of the pull request.
    """
    from settings import get_settings

    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pr = repo.create_pull(title=title, body=body, head=branch_id, base="main")
    settings = get_settings()
    if settings.reviewers:
        pr.create_review_request(reviewers=settings.reviewers)


def find_approved_prs(repo_name: str) -> List[int]:
    """Find pull requests that have been approved in a given repository."""
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
    """Attempt to merge a pull request with rebase if it is mergeable and rebaseable."""
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
    """Close an issue by its title in the specified repository."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="open")
    for issue in issues:
        if issue.title == issue_title:
            issue.edit(state="closed")
            break


def delete_branch_after_merge(g: Github, repo_name: str, branch) -> None:
    """Delete a branch in the given repository after a merge has occurred."""
    retries = 5
    while retries > 0:
        try:
            g.get_repo(repo_name).get_git_ref(f"heads/{branch.ref}").delete()
            break
        except Exception as e:
            print(e)
            retries -= 1
            time.sleep(2)


def fetch_open_issues(repo_name: str) -> list[Issue]:
    """Fetches open issues from a given repository."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="open")
    issue_data = [
        Issue(
            id=issue.id,
            number=issue.number,
            title=issue.title,
            description=issue.body,
            repository=repo_name,
            comments=[
                IssueComment(username=comment.user.login, content=comment.body)
                for comment in issue.get_comments()
            ],
            author=issue.user.login,
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
) -> None:
    repo = Repo(target_dir)
    repo.git.add("--all")
    repo.index.commit(f"{commit_subject}\n\n{commit_body}")


def get_all_checked_in_files(target_dir: str = os.getcwd()) -> List[str]:
    repo = Repo(target_dir)
    file_list = []
    for obj in repo.tree().traverse():
        if obj.type == "blob":
            file_list.append(obj.path)
    return file_list


def fetch_new_changes(target_dir: str = os.getcwd()) -> None:
    repo = Repo(target_dir)
    repo.git.fetch()


def is_issue_open(repo_name: str, issue_number: int) -> bool:
    """Checks if a given issue is still open."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(issue_number)
    return issue.state == "open"


def clone_repository(repo_url: str, path: str) -> None:
    """Clone the specified repository from GitHub to the specified path after ensuring the path is cleared."""
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)
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
    if not issue.body:
        return []
    issue_body = issue.body
    pattern = "#\\d+"
    matches = re.findall(pattern, issue_body)
    dependencies = [int(match.replace("#", "")) for match in matches]
    return dependencies


def check_dependency_issues(issue: Issue) -> bool:
    """Check if an issue has any open dependencies."""
    dependencies = get_issue_dependencies(issue.repository, issue.number)
    for dep in dependencies:
        if is_issue_open(issue.repository, dep):
            return True
    return False


def check_pr_conflict(repo_name: str, pr_id: int) -> bool:
    """Checks if a PR has a conflict."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_id)
    return not pr.mergeable


def git_reset(directory: str) -> None:
    """Reset the repository in the specified directory using the git reset command."""
    try:
        subprocess.check_call(["git", "reset", "--hard"], cwd=directory)
    except subprocess.CalledProcessError as e:
        raise Exception("git reset failed") from e


def find_git_repo(directory: str) -> str:
    """Find the .git directory in the specified directory or any of its parents."""
    while directory != os.path.dirname(directory):
        try:
            Repo(directory)
            return directory
        except Exception:
            pass
        directory = os.path.dirname(directory)
    return ""


def list_files(target_directory: str, gitignore_path: str) -> List[str]:
    """Lists all the files in a directory that aren't excluded by a gitignore file.

    Args:
        target_directory (str): The directory to search within.
        gitignore_path (str): The path to .gitignore file to apply exclusions.

    Returns:
        List[str]: List of file paths that are not ignored by .gitignore.
    """
    with open(gitignore_path, "r") as f:
        lines = f.readlines()
    lines.append(".git/")
    spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
    matches = []
    for root, dirs, files in os.walk(target_directory):
        for fname in files:
            full_path = os.path.join(root, fname)
            relative_path = os.path.relpath(full_path, start=target_directory)
            if not spec.match_file(relative_path):
                matches.append(relative_path)
    return matches


def repository_exists(repo_name: str) -> bool:
    """Check if a repository with the given name exists on GitHub.

    Args:
        repo_name (str): The name of the repository to check.

    Returns:
        bool: True if the repository exists, False otherwise.
    """
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    try:
        g.get_repo(repo_name)
        return True
    except:
        return False


def revert_commits(commit_hashes: List[str], target_dir: str = os.getcwd()) -> None:
    """Reverts a list of commits in the specified repository in descending order based on their commit times.

    Args:
        commit_hashes (List[str]): A list of commit SHA hashes to revert.
        target_dir (str): The directory of the repository where the commits will be reverted.
    """
    repo = Repo(target_dir)
    commits = [
        (repo.commit(hash_), repo.commit(hash_).committed_datetime)
        for hash_ in commit_hashes
    ]
    commits.sort(key=lambda x: x[1], reverse=True)
    for commit, _ in commits:
        try:
            repo.git.revert(commit, no_commit=True)
        except Exception as e:
            raise Exception(f"Failed to revert commit {commit.hexsha}: {str(e)}") from e
    repo.git.commit("-m", "Revert commits")


def list_commit_titles_and_authors(target_dir: str = os.getcwd()) -> List[str]:
    """List commit titles and authors for all commits in a repository at the specified path.

    Args:
        target_dir (str): Path to the repository. Defaults to the current working directory.

    Returns:
        List[str]: A list of strings with each entry in the format 'Commit title - Author email'
    """
    repo = Repo(target_dir)
    commit_info_list = []
    for commit in repo.iter_commits():
        title = commit.summary
        author_email = commit.author.email
        commit_info_list.append(f"{title} - {author_email}")
    return commit_info_list


def merge_with_squash(repo_name: str, pr_number: int, body: str) -> None:
    """Perform a squash merge on a pull request with a specified body and PR title as the commit title.

    Args:
            repo_name (str): The name of the repository.
            pr_number (int): The number of the pull request to merge.
            body (str): The body to use in the commit message.
    """
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.merge(merge_method="squash", commit_title=pr.title, commit_message=body)


def get_linked_issue(repo_name: str, pr_id: int) -> Optional[Issue]:
    """Retrieves the Issue linked to a given pull request in the specified repository.

    Args:
        repo_name (str): The name of the repository containing the pull request.
        pr_id (int): The unique identifier of the pull request.

    Returns:
        Optional[Issue]: The Issue object linked to the pull request, or None if no linked issue is found.
    """
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_id)
    linked_issue_number = None
    match = re.search("#(\\d+)", pr.body)
    if match:
        linked_issue_number = int(match.group(1))
    if linked_issue_number:
        issue = repo.get_issue(linked_issue_number)
        return Issue(
            id=issue.id,
            number=issue.number,
            title=issue.title,
            description=issue.body,
            repository=repo_name,
            comments=[
                IssueComment(username=comment.user.login, content=comment.body)
                for comment in issue.get_comments()
            ],
            author=issue.user.login,
        )
    return None
