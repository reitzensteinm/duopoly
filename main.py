import os
from github import Github
import openai
import re
from black import FileMode, format_str
import fnmatch
import command

import gpt
from gpt import SYSTEM_CHECK
from utils import read_file, write_file


def format_python_code(code: str) -> str:
    formatted_code = format_str(code, mode=FileMode())
    return formatted_code


def find_python_files() -> list[str]:
    python_files = []

    for root, dirnames, filenames in os.walk("."):
        for filename in fnmatch.filter(filenames, "*.py"):
            if "venv" not in root:
                python_files.append(os.path.join(root, filename))

    return python_files


from utils import read_file, write_file, partition_by_predicate, add_line_numbers

from gpt import gpt_query
from repo import fetch_open_issues
from patch import patch_files, apply_patch


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


import uuid


def command_loop(prompt: str, files: dict) -> dict:
    new_files = files.copy()

    scratch = ""

    # Sanity limit of 10
    for _ in range(10):
        response = gpt_query(f"Instructions: {prompt}\n{scratch}", gpt.SYSTEM_COMMAND)
        commands = command.parse_command_string(response)

        for c in commands:
            comm = c["command"]
            scratch += "\n".join([">> " + line for line in command.command_to_str(c).split("\n")]) + "\n"

            if comm == "FILE":
                scratch += add_line_numbers(files[c["path"]]) + "\n"
            elif comm == "UPDATE":
                new_files[c["path"]] = c["body"]
            elif comm == "FINISH":
                return new_files


def apply_prompt_to_files(prompt: str, files: dict) -> dict:
    issue_description = prompt  # f"{str(uuid.uuid4())}\n{prompt}"
    old_files = files

    new_files = command_loop(
        f"Instructions: {issue_description}\nFiles:\n{list_files(old_files)}", files
    )

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
        issue_description,
    )

    return new_files


from repo import Issue
import repo


def process_issue(issue: Issue) -> None:
    files = {f: read_file(f) for f in find_python_files()}
    branch_id = f"issue-{issue.id}"
    repo.switch_and_reset_branch(branch_id)
    updated_files = apply_prompt_to_files(issue.description, files)

    for k, v in updated_files.items():
        write_file(k, v)

    import subprocess

    result = subprocess.run(
        ["pytest", "-ra", "--log-file=pytest_errors.log"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        with open("pytest_errors.log", "r") as file:
            errors = file.read()
        raise Exception("Pytest failed\n" + errors)
    repo.commit_local_modifications(issue.title, f'Prompt: "{issue.description}"')
    repo.push_local_branch_to_origin(branch_id)
    if not repo.check_pull_request_title_exists("reitzensteinm/duopoly", issue.title):
        repo.create_pull_request(
            repo_name="reitzensteinm/duopoly",
            branch_id=branch_id,
            title=issue.title,
            body=issue.description,
        )


from termcolor import cprint


def main(retries=5) -> None:
    for issue in fetch_open_issues("reitzensteinm/duopoly"):
        retry_count = 0
        while retry_count < retries:
            cprint(f"Attempt {retry_count + 1}", "magenta")
            try:
                process_issue(issue)
                break
            except Exception as e:
                retry_count += 1
                cprint(str(e), "red")
                if retry_count == retries:
                    print(f"Failed to process issue {issue.id} after {retries} retries")
    repo.switch_and_reset_branch("main")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--retries", type=int, default=5, help="number of retries (default is 5)"
    )
    args = parser.parse_args()
    main(retries=args.retries)
