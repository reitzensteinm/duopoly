from tools.imports import imports
from black import FileMode, format_str
import os
import uuid
import subprocess
from gpt import SYSTEM_CHECK, gpt_query
import gpt
from utils import read_file, write_file, add_line_numbers
import command
import repo
import shutil
from repo import Issue


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
    trimmed_string = string.strip()
    lines = trimmed_string.split("\n")
    if lines[0].startswith("```") and lines[-1].startswith("```"):
        return "\n".join(lines[1:-1])
    else:
        return string


def synchronize_files(target_dir, old_files, updated_files):
    for k, v in updated_files.items():
        write_file(os.path.join(target_dir, k), v)

    deleted_files = [f for f in old_files.keys() if f not in updated_files]
    for f in deleted_files:
        os.remove(f)


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
            elif comm == "IMPORTS":
                file_contents = files.get(c["path"], "")
                if c["path"].endswith(".py"):
                    imports_result = imports(file_contents)
                    scratch += f"```python\n{imports_result}\n```\n"
            elif comm == "FINISH":
                return new_files
    raise Exception("Command Loop Overflow")


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
    if not repo.is_issue_open("reitzensteinm/duopoly", issue.number):
        return

    if repo.check_issue_has_open_pr_with_same_title(
        "reitzensteinm/duopoly", issue.title
    ):
        return

    target_dir = f"target/issue-{issue.number}"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    repo.clone_repository("https://github.com/reitzensteinm/duopoly.git", target_dir)

    branch_id = f"issue-{issue.id}"

    if not dry_run:
        repo.switch_and_reset_branch(branch_id, target_dir)

    files = {
        f: read_file(os.path.join(target_dir, f))
        for f in repo.get_all_checked_in_files(target_dir)
    }

    updated_files = apply_prompt_to_files(issue.description, files)
    synchronize_files(target_dir, files, updated_files)

    pylint_result = subprocess.run(
        ["pylint", "--disable=R,C,W", os.path.join(target_dir, "src")],
        capture_output=True,
        text=True,
    )
    print(pylint_result.stdout)
    if pylint_result.returncode != 0:
        raise Exception("Pylint failed\n" + pylint_result.stdout)

    result = subprocess.run(
        ["pytest", os.path.join(target_dir, "src"), "-rf"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception("Pytest failed\n" + result.stdout)

    if not dry_run:
        repo.commit_local_modifications(
            issue.title, f'Prompt: "{issue.description}"', target_dir
        )
        repo.push_local_branch_to_origin(branch_id, target_dir)
        if not repo.check_pull_request_title_exists(
            "reitzensteinm/duopoly", issue.title
        ):
            repo.create_pull_request(
                repo_name="reitzensteinm/duopoly",
                branch_id=branch_id,
                title=issue.title,
                body=issue.description,
            )
