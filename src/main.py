import argparse
import traceback
import time
from concurrent.futures import ThreadPoolExecutor
from termcolor import cprint
from pipeline.issue import process_issue
import repo
from evals.evals import process_evals
from tracing.trace import create_trace, bind_trace, trace
from tracing.tags import EXCEPTION
import ast
import astor

MAX_RETRIES = 1


def merge_approved_prs() -> None:
    approved_prs = repo.find_approved_prs("reitzensteinm/duopoly")
    for pr_id in approved_prs:
        for attempt in range(5):
            if repo.merge_with_rebase_if_possible("reitzensteinm/duopoly", pr_id):
                print(f"Merged PR: {pr_id}")
                break
            else:
                print(f"Attempt {attempt + 1}: Could not merge PR: {pr_id}")
                if attempt < 4:
                    time.sleep(5)
                else:
                    print(f"Failed to merge PR {pr_id} after 5 attempts.")
    repo.fetch_new_changes()


def replace_function_in_code(source_code, function_name, new_function_code):
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            new_function_node = ast.parse(new_function_code)
            node.body = new_function_node.body
    updated_code = astor.to_source(tree)
    return updated_code


def main(dry_run=False, issue_name=None) -> None:
    if not dry_run:
        merge_approved_prs()
    open_issues = repo.fetch_open_issues("reitzensteinm/duopoly")

    def process_open_issue(issue):
        if repo.check_dependency_issues("reitzensteinm/duopoly", issue.number):
            cprint(f"Not processing issue {issue.number}: blocked", "yellow")
            return
        if issue_name is None or issue_name in issue.title:
            for attempt in range(MAX_RETRIES):
                trace_instance = create_trace(f"{issue.title}")
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
    with ThreadPoolExecutor(max_workers=5) as executor:
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
        main(dry_run=args.dry_run, issue_name=args.issue)
