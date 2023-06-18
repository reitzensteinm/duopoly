import argparse
import traceback
import time
from concurrent.futures import ThreadPoolExecutor
from termcolor import cprint
from pipeline.issue import process_issue
import repo
from evals.evals import process_evals
from tracing.trace import create_trace, bind_trace


def merge_approved_prs() -> None:
    approved_prs = repo.find_approved_prs("reitzensteinm/duopoly")
    for pr_id in approved_prs:
        if repo.merge_with_rebase_if_possible("reitzensteinm/duopoly", pr_id):
            print(f"Merged PR: {pr_id}")
            time.sleep(30)
        else:
            print(f"Could not merge PR: {pr_id}")
    repo.fetch_new_changes()


def main(dry_run=False) -> None:
    if not dry_run:
        merge_approved_prs()

    open_issues = repo.fetch_open_issues("reitzensteinm/duopoly")

    def process_open_issue(issue):
        trace = create_trace(f"Issue {issue.id}")
        bind_trace(trace)
        try:
            process_issue(issue, dry_run)
        except Exception as e:
            cprint(f"{str(e)}\n{traceback.format_exc()}", "red")
            print(f"Failed to process issue {issue.id}")

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
        main(dry_run=args.dry_run)
