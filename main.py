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


def patch_files(patch: str):
    # This is a hack - patches will be ignored if the file doesn't exist
    pattern = r"@@PATCH@@ (.+) (\d+) (\d+)"
    for l in patch.split("\n"):
        match = re.search(pattern, l)
        if match:
            yield match.group(1)


def apply_patch(file_name: str, file: str, patch: str) -> str:
    """Applies the given patch to the file contents."""
    pattern = r"@@PATCH@@ (.+) (\d+) (\d+)"

    def apply_patch_inner(file_lines, patch_lines, off):
        match = re.search(pattern, patch_lines[0])
        patch_file = match.group(1)

        if patch_file != file_name:
            return off, file_lines

        start = int(match.group(2)) + off
        end = int(match.group(3)) + off
        off = off + ((len(patch_lines) - 1) - (1 + end - start))
        return off, file_lines[0 : start - 1] + patch_lines[1:] + file_lines[end:]

    file_lines = file.split("\n")
    patch_lines = patch.split("\n")
    offset = 0

    patches = partition_by_predicate(patch_lines, lambda l: re.search(pattern, l))
    patches.sort(key=lambda p: int(re.search(pattern, p[0]).group(2)))

    for p in patches:
        offset, file_lines = apply_patch_inner(file_lines, p, offset)

    return "\n".join(file_lines)


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

    repo.commit_local_modifications()
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
        process_issue(issue)
    repo.switch_and_reset_branch("main")


if __name__ == "__main__":
    main()
