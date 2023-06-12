import os
import re
import fnmatch
import uuid
import subprocess
import argparse
import traceback
from github import Github
import openai
from black import FileMode, format_str
from termcolor import cprint
import command
import gpt
import repo
from utils import read_file, write_file, partition_by_predicate, add_line_numbers
from gpt import SYSTEM_CHECK, gpt_query
from repo import fetch_open_issues, Issue, get_all_checked_in_files, fetch_new_changes
from patch import patch_files, apply_patch


def format_python_code(code: str) -> str:
    formatted_code = format_str(code, mode=FileMode())
    return formatted_code


def check_result(old, new, prompt) -> bool:
    result = gpt_query(
        f"ORIGINAL:\n{old}\nMODIFIED:\n{new}\nOBJECTIVE:\n{prompt}", SYSTEM_CHECK
    )

    if not "VERDICT: OK" in result:
        print(new)
        raise Exception(result)

    return True


def list_files(files):
    file_info = ""
    for k, v in files.items():
        file_info += f"{k}:\n{add_line_numbers(v)}\n"
    return file_info


def remove_markdown_quotes(string: str) -> str:
    lines = string.split("\n")
    if lines[0].startswith("```") and lines[-1].startswith("```"):
        return "\n".join(lines[1:-1])
    else:
        return string


def command_loop(prompt: str, files: dict) -> dict:
    new_files = files.copy()

    scratch = "Available files: " + ", ".join(files.keys()) + "\n"

    for _ in range(10):
        response = gpt_query(f"Instructions: {prompt}\n{scratch}", gpt.SYSTEM_COMMAND)
        commands = command.parse_command_string(response)

        for c in commands:
            comm = c["command"]
            scratch += (
                "\n".join(
                    [">> " + line for line in command.command_to_str(c).split("\n")]
                )
                + "\n"
            )

            if comm == "FILE":
                contents = files.get(c["path"], "")
                scratch += f"```python\n{contents}\n```\n"
            elif comm == "UPDATE":
                updated_content = c["body"]
                updated_content = remove_markdown_quotes(updated_content)
                if c["path"].endswith(".py"):
                    updated_content = format_python_code(updated_content)
                new_files[c["path"]] = updated_content
            elif comm == "DELETE":
                if c["path"] in new_files:
                    del new_files[c["path"]]
            elif comm == "FINISH":
                return new_files


def apply_prompt_to_files(prompt: str, files: dict) -> dict:
    old_files = files

    new_files = command_loop(f"{str(uuid.uuid4())}\n{prompt}", files)

    old_files_filtered = {
        k: v
        for k, v in old_files.items()
        if k in new_files and v != new_files[k] or k not in new_files
    }
    new_files_filtered = {
        k: v
        for k, v in new_files.items()
        if k in old_files and v != old_files[k] or k not in old_files
    }
    check_result(
        list_files(old_files_filtered),
        list_files(new_files_filtered),
        prompt,
    )

    return new_files


def process_issue(issue: Issue, dry_run: bool) -> None:
    files = {f: read_file(f) for f in get_all_checked_in_files()}
    branch_id = f"issue-{issue.id}"

    if not dry_run:
        repo.switch_and_reset_branch(branch_id)

    updated_files = apply_prompt_to_files(issue.description, files)

    for k, v in updated_files.items():
        write_file(k, v)

    deleted_files = [f for f in files.keys() if f not in updated_files]
    for f in deleted_files:
        os.remove(f)

    result = subprocess.run(
        ["pytest", "-rf"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception("Pytest failed\n" + result.stdout)

    if not dry_run:
        repo.commit_local_modifications(issue.title, f'Prompt: "{issue.description}"')
        repo.push_local_branch_to_origin(branch_id)
        if not repo.check_pull_request_title_exists(
            "reitzensteinm/duopoly", issue.title
        ):
            repo.create_pull_request(
                repo_name="reitzensteinm/duopoly",
                branch_id=branch_id,
                title=issue.title,
                body=issue.description,
            )


def merge_approved_prs() -> None:
    approved_prs = repo.find_approved_prs("reitzensteinm/duopoly")
    for pr_id in approved_prs:
        if repo.merge_with_rebase_if_possible("reitzensteinm/duopoly", pr_id):
            print(f"Merged PR: {pr_id}")
        else:
            print(f"Could not merge PR: {pr_id}")
    repo.fetch_new_changes()


def main(retries=3, dry_run=False) -> None:
    for issue in fetch_open_issues("reitzensteinm/duopoly"):
        if not dry_run:
            merge_approved_prs()
        retry_count = 0
        while retry_count < retries:
            cprint(f"Attempt {retry_count + 1}", "magenta")
            try:
                process_issue(issue, dry_run)
                break
            except Exception as e:
                retry_count += 1
                cprint(f"{str(e)}\n{traceback.format_exc()}", "red")
                if retry_count == retries:
                    print(f"Failed to process issue {issue.id} after {retries} retries")
        if not dry_run:
            repo.switch_and_reset_branch("main")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--retries", type=int, default=3, help="number of retries (default is 3)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Activate dry run mode")
    args = parser.parse_args()
    main(retries=args.retries, dry_run=args.dry_run)
