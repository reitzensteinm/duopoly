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
    """
    Try to merge a pull request in the specified repository.
    If there's a conflict or merging fails, it returns False; otherwise, it returns True if the merge is successful.

    :param repository: The repository where the pull request exists.
    :param pr_id: The ID of the pull request to be merged.
    :return: Boolean indicating if the merge was successful or not.
    """
    if repo.check_pr_conflict(repository, pr_id):
        cprint(f"PR {pr_id} has conflicts. Skipping merge.", "red")
        return False
    if repo.merge_with_rebase_if_possible(repository, pr_id):
        print(f"Merged PR: {pr_id}")
        return True
    else:
        return False


def merge_approved_prs(repository: str) -> None:
    """
    Merges all approved pull requests for the given repository.
    Attempts to merge each pull request once and retries once more if the first attempt fails.

    :param repository: The repository to merge approved pull requests in.
    :return: None
    """
    approved_prs = repo.find_approved_prs(repository)
    for pr_id in approved_prs:
        if not try_merge_pr(repository, pr_id):
            print(f"Attempt 1: Could not merge PR: {pr_id}, retrying...")
            time.sleep(5)
            if not try_merge_pr(repository, pr_id):
                print(f"Failed to merge PR {pr_id} after 2 attempts.")
    repo.fetch_new_changes()


def process_repository(
    dry_run: bool = False, issue_name: str = None, repository: str = ""
) -> None:
    """
    Processes all issues for the specified repository.
    It will retry processing an issue once if it fails on the first try.

    :param dry_run: Flag to simulate processing without making any changes.
    :param issue_name: The name of the specific issue to process, or None to process all issues.
    :param repository: The repository whose issues are to be processed.
    :return: None
    """
    if not repo.repository_exists(repository):
        print(f'Warning: The repository "{repository}" does not exist.')
        return
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
                    f"""Attempt 1 failed for issue {issue.title} with error: {str(e)}
{traceback.format_exc()}""",
                    "red",
                )
                trace(EXCEPTION, str(e))
                print(f"Retrying to process issue {issue.title}...")
                try:
                    process_issue(issue, dry_run)
                except Exception as e:
                    cprint(
                        f"Failed to process issue {issue.title} after 2 attempts with error: {str(e)}",
                        "red",
                    )
                    trace(EXCEPTION, str(e))
                    raise

    if dry_run:
        process_open_issue(open_issues[0])
    else:
        if not dry_run:
            merge_approved_prs(repository)
        with ThreadPoolExecutor(
            max_workers=settings.get_settings().max_workers
        ) as executor:
            list(executor.map(process_open_issue, open_issues))


def evals(directory: str) -> None:
    """
    Processes evaluation of the provided directory using the eval module.

    :param directory: The directory containing the evaluation data to be processed.
    :return: None
    """
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
    if args.experimentation:
        from tools.experiment import run_experimentation

        run_experimentation(args.experimentation)
        sys.exit(0)
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
