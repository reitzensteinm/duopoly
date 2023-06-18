import argparse
import traceback
from termcolor import cprint
from pipeline.issue import process_issue
import repo


def merge_approved_prs() -> None:
    approved_prs = repo.find_approved_prs("reitzensteinm/duopoly")
    for pr_id in approved_prs:
        if repo.merge_with_rebase_if_possible("reitzensteinm/duopoly", pr_id):
            print(f"Merged PR: {pr_id}")
        else:
            print(f"Could not merge PR: {pr_id}")
    repo.fetch_new_changes()


def main(dry_run=False) -> None:
    if not dry_run:
        merge_approved_prs()

    for issue in repo.fetch_open_issues("reitzensteinm/duopoly"):
        try:
            process_issue(issue, dry_run)
        except Exception as e:
            cprint(f"{str(e)}\n{traceback.format_exc()}", "red")
            print(f"Failed to process issue {issue.id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Activate dry run mode")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
