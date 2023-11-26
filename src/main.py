import argparse
import traceback
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from termcolor import cprint
from pipeline.issue import process_issue
import repo
from evals.evals import process_evals
from tracing.trace import create_trace, bind_trace, trace
from website.analysis import print_analysis
from tracing.tags import EXCEPTION
import os
import ast
import astor
import settings


def try_merge_pr(repository, pr_id):
    if repo.check_pr_conflict(repository, pr_id):
        cprint(f"PR {pr_id} has conflict. Skipping merge.", "red")
        return False
    if repo.merge_with_rebase_if_possible(repository, pr_id):
        print(f"Merged PR: {pr_id}")
        return True
    else:
        return False


def try_squash_merge_pr(repository: str, pr_id: int) -> bool:
    """
    Attempts to squash merge a pull request using the PR title as the commit title, and setting the commit message to the linked Issue body.

    :param repository: The repository where the pull request resides.
    :param pr_id: The ID of the pull request to be merged.
    :return: True if the squash merge was successful, False otherwise.
    """
    pr = repo.get_pull_request(repository, pr_id)
    if not pr:
        cprint(f"PR {pr_id} not found. Skipping squash merge.", "yellow")
        return False
    linked_issue = repo.get_linked_issue_from_pr(pr)
    if not linked_issue:
        cprint(f"PR {pr_id} has no linked issue. Skipping squash merge.", "yellow")
        return False
    commit_message = f"Prompt: {linked_issue.description}"
    return repo.merge_with_squash(repository, pr_id, pr.title, commit_message)


def merge_approved_prs(repository) -> None:
    is_merged = False
    approved_prs = repo.find_approved_prs(repository)
    for pr_id in approved_prs:
        for attempt in range(5):
            if try_squash_merge_pr(repository, pr_id):
                is_merged = True
                break
            else:
                print(f"Attempt {attempt + 1}: Could not merge PR: {pr_id}")
                if attempt < 4:
                    time.sleep(5)
        if not is_merged:
            print(f"Failed to merge PR {pr_id} after 5 attempts.")
    if is_merged:
        sys.exit(0)
    repo.fetch_new_changes()


def process_repository(dry_run=False, issue_name=None, repository="") -> None:
    if not repo.repository_exists(repository):
        print(f'Warning: The repository "{repository}" does not exist.')
        return
    if not dry_run:
        merge_approved_prs(repository)
    open_issues = repo.fetch_open_issues(repository)

    def process_open_issue(issue):
        if repo.check_dependency_issues(issue):
            cprint(f"Not processing issue {issue.number}: blocked", "yellow")
            return
        if issue_name is None or issue_name in issue.title:
            trace_instance = create_trace(issue.title)
            bind_trace(trace_instance)
            try:
                process_issue(issue, dry_run)
            except Exception as e:
                cprint(
                    f"""Failed processing issue {issue.title} with error: {str(e)}
				{traceback.format_exc()}""",
                    "red",
                )
                trace(EXCEPTION, str(e))
                raise

    if dry_run:
        process_open_issue(open_issues[0])
        return
    with ThreadPoolExecutor(
        max_workers=settings.get_settings().max_workers
    ) as executor:
        results = executor.map(process_open_issue, open_issues)
    for result in results:
        pass


def evals(directory: str) -> None:
    process_evals(directory)


def try_squash_merge_pr(repository: str, pr_id: int) -> bool:
    """
    Attempt to perform a squash merge on a pull request identified by the pr_id in the given repository.

    Retrieves the title of the pull request, looks for the linked issue by examining the pull request description,
    and formats the commit message as "Prompt: <Issue body>". Uses the title of the pull request as the commit title.
    The merge is performed using the squash method.

    Args:
            repository (str): The name of the repository containing the pull request.
            pr_id (int): The identifier of the pull request to be merged.

    Returns:
            bool: True if the squash merge was successful, False otherwise.
    """
    from repo import merge_with_squash, find_linked_issue_for_pr

    linked_issue = find_linked_issue_for_pr(repository, pr_id)
    if linked_issue is None:
        print(f"No linked issue found for PR {pr_id}.")
        return False
    commit_message = f"Prompt: {linked_issue.description}"
    try:
        merge_with_squash(repository, pr_id, commit_message)
        return True
    except Exception as e:
        print(f"Failed to squash merge PR {pr_id}: {str(e)}")
        return False


if __name__ == "__main__":
    main()
