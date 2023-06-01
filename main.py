import os
from github import Github
import openai
import re
from black import FileMode, format_str
import fnmatch
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


from utils import read_file, write_file, partition_by_predicate

from gpt import gpt_query

from repo import fetch_open_issues

from utils import read_file, write_file, partition_by_predicate, add_line_numbers


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


def apply_prompt_to_files(prompt: str, files: dict) -> dict:
    old_files = files
    patch = gpt_query(f"Instructions: {prompt}\nFiles:\n{list_files(old_files)}")

    new_files = old_files.copy()

    for f in patch_files(patch):
        if f not in new_files:
            new_files[f] = ""

    for f in new_files:
        old = new_files[f]
        new = format_python_code(apply_patch(f, old, patch))
        new_files[f] = new

    check_result(list_files(old_files), list_files(new_files), prompt)

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

    repo.commit_local_modifications(issue.title, f'Prompt: "{issue.description}"')
    repo.push_local_branch_to_origin(branch_id)

    if not repo.check_pull_request_title_exists("reitzensteinm/duopoly", issue.title):
        repo.create_pull_request(
            repo_name="reitzensteinm/duopoly",
            branch_id=branch_id,
            title=issue.title,
            body=issue.description,
        )


def main() -> None:
    for issue in fetch_open_issues("reitzensteinm/duopoly"):
        retries = 0
        while retries < 5:
            try:
                process_issue(issue)
                break
            except Exception as e:
                retries += 1
                if retries == 5:
                    print(f"Failed to process issue {issue.id} after 5 retries")
    repo.switch_and_reset_branch("main")


if __name__ == "__main__":
    main()
