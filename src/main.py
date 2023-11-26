import argparse
import traceback
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
import settings


def try_merge_pr(repository: str, pr_id: int) -> bool:
    """
    Attempt to merge a pull request after checking for conflicts.

    :param repository: A string representing the repository name.
    :param pr_id: The pull request ID to merge.
    :return: A boolean indicating whether the merge was successful.
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
    Merge all approved pull requests for the specified repository.

    :param repository: A string representing the repository name.
    :return: None.
    """
    is_merged = False
    approved_prs = repo.find_approved_prs(repository)
    for pr_id in approved_prs:
        is_merged = try_merge_pr(repository, pr_id)
        if is_merged:
            break
    if is_merged:
        sys.exit(0)
    repo.fetch_new_changes()


def process_repository(
    dry_run: bool = False, issue_name: str = None, repository: str = ""
) -> None:
    """
    Process the repository by merging approved PRs and processing open issues.

    :param dry_run: A boolean switch to activate dry run mode.
    :param issue_name: A string to identify a specific issue by name.
    :param repository: A string representing the repository name.
    :return: None.
    """
    if not repo.repository_exists(repository):
        print(f'Warning: The repository "{repository}" does not exist.')
        return
    if not dry_run:
        merge_approved_prs(repository)
    open_issues = repo.fetch_open_issues(repository)

    def process_open_issue(issue):
        """
        Process a single open issue.

        The function checks if the issue is blocked by dependency issues and processes it if not blocked.
        It creates a trace for debugging and processing information.

        :param issue: The issue to be processed.
        :return: None.
        """
        if repo.check_dependency_issues(issue):
            cprint(
                f"Not processing issue {issue.number}: Blocked by dependency issues.",
                "yellow",
            )
            return
        trace_inst = create_trace(issue.title)
        bind_trace(trace_inst)
        try:
            process_issue(issue, dry_run)
        except Exception as e:
            cprint(f"Exception raised while processing issue {issue.title}: {e}", "red")
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
    """
    Process evaluations from the given directory.

    :param directory: A string representing the path to the evaluation directory.
    :return: None.
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
