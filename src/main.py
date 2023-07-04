import argparse
import traceback
import time
from concurrent.futures import ThreadPoolExecutor
from termcolor import cprint
from pipeline.issue import process_issue
import repo
from evals.evals import process_evals
from tracing.trace import create_trace, bind_trace

MAX_RETRIES = (
    3  # Maximum number of retries if exception is thrown in process_open_issue
)


def merge_approved_prs() -> None:
    approved_prs = repo.find_approved_prs("reitzensteinm/duopoly")
    for pr_id in approved_prs:
        for attempt in range(
            5
        ):  # Attempt to merge the pull request for a maximum of 5 times
            if repo.merge_with_rebase_if_possible("reitzensteinm/duopoly", pr_id):
                print(f"Merged PR: {pr_id}")
                break  # Break out of the retry loop
            else:
                print(f"Attempt {attempt + 1}: Could not merge PR: {pr_id}")
                if attempt < 4:  # If this wasn't the last attempt
                    time.sleep(
                        5
                    )  # Sleep for 5 seconds before trying again, if this wasn't the last attempt
                else:
                    print(
                        f"Failed to merge PR {pr_id} after 5 attempts."
                    )  # If we've used all our retries
    repo.fetch_new_changes()


def main2(dry_run=False, issue_name=None) -> None:  # renaming function name to main2
    if not dry_run:
        merge_approved_prs()
    open_issues = repo.fetch_open_issues("reitzensteinm/duopoly")

    def process_open_issue(issue):
        if issue_name is None or issue_name in issue.title:
            for attempt in range(MAX_RETRIES):
                trace = create_trace(f"Issue {issue.id}")
                bind_trace(trace)
                try:
                    process_issue(issue, dry_run)
                    break  # Breaking out of the loop if the process_issue is successful
                except Exception as e:
                    cprint(
                        f"Attempt {attempt + 1} failed for issue {issue.id} with error: {str(e)}\n{traceback.format_exc()}",
                        "red",
                    )
                    # If we've used all our retries, then rethrow the exception
                    if attempt == MAX_RETRIES - 1:
                        print(
                            f"Failed to process issue {issue.id} after {MAX_RETRIES} attempts."
                        )
                        raise
                    else:
                        print(f"Retrying to process issue {issue.id}...")

    with ThreadPoolExecutor() as executor:
        results = executor.map(process_open_issue, open_issues)

    for result in results:
        pass


def evals(directory: str) -> None:
    process_evals(directory)


if __name__ == "__main__":
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
    args = parser.parse_args()
    if args.evals:
        evals(args.evals)
    else:
        main2(
            dry_run=args.dry_run, issue_name=args.issue
        )  # calling main2 instead of main
