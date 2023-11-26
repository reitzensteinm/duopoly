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


def try_merge_pr(repository: str, pr_id: int) -> bool:
    """Attempt to merge a pull request.

    This function checks for conflicts and attempts to merge a pull request with a rebase if possible.

    :param repository: The name of the repository containing the pull request.
    :param pr_id: The ID of the pull request to merge.
    :return: True if the pull request was successfully merged, False otherwise.
    """
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
    Attempts to perform a squash merge on the specified pull request using its title for the commit title and the linked issue's body with 'Prompt: ' as the commit description.

    The 'repository' argument identifies the GitHub repository, while 'pr_id' is the identifier for the pull request. Returns True if the merge operation is successful, False otherwise.
    """
    pr_details = repo.get_pull_request_details(repository, pr_id)
    if not pr_details:
        cprint(f"Pull Request #{pr_id} not found in '{repository}'.", "red")
        return False
    issue_body = repo.get_issue_body(repository, pr_details["linked_issue_number"])
    if not issue_body:
        cprint(f"No linked Issue found for PR #{pr_id}.", "red")
        return False
    commit_message = f"Prompt: {issue_body}"
    try:
        repo.merge_with_squash(repository, pr_id, pr_details["title"], commit_message)
        print(f"Squashed and merged PR #{pr_id} into '{repository}'.")
        return True
    except Exception as e:
        cprint(f"Failed to squash and merge PR #{pr_id}: {e}", "red")
        return False


def merge_approved_prs(repository) -> None:
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


def main() -> None:
    """
    Entry point of the application which parses command-line arguments and initiates corresponding actions.

    The function supports running the application in various modes, such as dry run, analysis, context,
    and evaluations, through the use of command-line arguments. The --use-tools flag enables the use
    of the new OpenAI tools API.

    :return: None
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
    parser.add_argument(
        "--quality-checks",
        action="store_true",
        help="Activate quality checks mode",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--use-tools",
        action="store_true",
        help="Enable the use of the new OpenAI tools API",
    )
    args = parser.parse_args()
    settings.PARSED_ARGS = vars(args)
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
        for repository in settings.REPOSITORY_PATH:
            process_repository(
                dry_run=args.dry_run, issue_name=args.issue, repository=repository
            )


if __name__ == "__main__":
    main()
