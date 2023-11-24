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
from settings import get_settings, REPOSITORY_PATH

MAX_RETRIES = 1


def try_merge_pr(repository: str, pr_id: int) -> bool:
    """
    Attempt to merge a pull request on the given repository.

    This function checks for conflicts and attempts a rebase merge.

    Arguments:
        repository: A string representing the repository name.
        pr_id: An integer representing the ID of the pull request to merge.

    Returns:
        A boolean indicating success or failure of the merge.
    """
    if repo.check_pr_conflict(repository, pr_id):
        cprint(f"PR {pr_id} has conflict. Skipping merge.", "red")
        return False
    if repo.merge_with_rebase_if_possible(repository, pr_id):
        print(f"Merged PR: {pr_id}")
        return True
    else:
        return False


def merge_approved_prs(repository: str) -> None:
    """
    Merge all approved pull requests for the given repository.

    This function finds all approved pull requests and attempts to merge them.

    Arguments:
        repository: A string representing the repository name where PRs will be merged.

    Returns:
        None.
    """
    is_merged = False
    approved_prs = repo.find_approved_prs(repository)
    for pr_id in approved_prs:
        for attempt in range(5):
            if try_merge_pr(repository, pr_id):
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


def process_repository(
    dry_run: bool = False, issue_name: str = None, repository: str = ""
) -> None:
    """
    Process the given repository, merging PRs and processing issues.

    If not in dry run mode, it merges approved pull requests and processes open issues.

    Arguments:
        dry_run: A boolean indicating whether to perform a dry run.
        issue_name: An optional string filtering issues by name.
        repository: A string defining the repository to process.

    Returns:
        None.
    """
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
            for attempt in range(MAX_RETRIES):
                trace_instance = create_trace(issue.title)
                bind_trace(trace_instance)
                try:
                    process_issue(issue, dry_run)
                    break
                except Exception as e:
                    cprint(
                        f"""Attempt {attempt + 1} failed for issue {issue.title} with error: {str(e)}
						{traceback.format_exc()}""",
                        "red",
                    )
                    trace(EXCEPTION, str(e))
                    if attempt == MAX_RETRIES - 1:
                        print(
                            f"Failed to process issue {issue.title} after {MAX_RETRIES} attempts."
                        )
                        raise
                    else:
                        print(f"Retrying to process issue {issue.title}...")

    if dry_run:
        process_open_issue(open_issues[0])
        return
    with ThreadPoolExecutor(max_workers=get_settings().max_workers) as executor:
        results = executor.map(process_open_issue, open_issues)
    for result in results:
        pass


def evals(directory: str) -> None:
    """
    Process evaluations for a given directory.

    This function runs evaluations specified within the directory.

    Arguments:
        directory: A string representing the directory containing evaluation tests.

    Returns:
        None.
    """
    process_evals(directory)


def main() -> None:
    """
    Main function for running the script.

    It parses command-line arguments and activates different modes based on those arguments.

    Arguments:
        None.

    Returns:
        None.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Activate dry run mode")
    parser.add_argument(
        "--issue", type=str, help="Specify the issue name", required=False, default=None
    )
    parser.add_argument(
        "--evals",
        type=str,
        help="Specify the eval directory",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--analysis", action="store_true", help="Activate analysis mode"
    )
    parser.add_argument("--context", action="store_true", help="Activate context mode")
    args = parser.parse_args()
    if args.analysis:
        repo_dir = os.getcwd()
        print_analysis(repo_dir)
        sys.exit(0)
    if args.context:
        from context.repl import repl

        repl()
        sys.exit(0)
    if args.evals:
        evals(args.evals)
    else:
        for repository in REPOSITORY_PATH:
            process_repository(
                dry_run=args.dry_run, issue_name=args.issue, repository=repository
            )


if __name__ == "__main__":
    main()
