from tools.imports import imports
from tools.search import search_tool  # Importing search_tool
from tools.pylint import run_pylint  # Importing run_pylint
from tools.pytest import run_pytest  # Importing run_pytest
from black import FileMode, format_str
import os
import uuid
import subprocess
import gpt
from utils import read_file, write_file, add_line_numbers
from commands import command
from commands.commands import (
    Think,
    Verdict,
    Files,
    ReplaceFile,
    Search,
    DeleteFile,
    COMMANDS_CHECK,
    COMMANDS_GENERATE,
)  # Importing all commands
from commands.loop import command_loop_new  # Importing command_loop_new
import repo
import shutil
from repo import Issue

CHECK_OPEN_PR = False


def format_python_code(code: str) -> str:
    formatted_code = format_str(code, mode=FileMode())
    return formatted_code


def check_result(old, new, prompt) -> bool:
    command, state = command_loop_new(
        f"ORIGINAL:\n{old}\nMODIFIED:\n{new}\nOBJECTIVE:\n{prompt}",
        gpt.SYSTEM_CHECK_FUNC,
        COMMANDS_CHECK,
    )

    if not command.verdict:
        raise Exception("NEGATIVE VERDICT: " + command.reasoning)

    return command.verdict


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
        os.remove(os.path.join(target_dir, f))


def apply_prompt_to_files(prompt: str, files: dict) -> dict:
    old_files = files
    scratch = "Available files: " + ", ".join(files.keys()) + "\n"
    command, state = command_loop_new(
        scratch + f"{str(uuid.uuid4())}\n{prompt}",
        gpt.SYSTEM_COMMAND_FUNC,
        COMMANDS_GENERATE,
        files,
    )

    old_files_filtered = {
        k: v
        for k, v in old_files.items()
        if k in state.files and v != state.files[k] or k not in state.files
    }
    new_files_filtered = {
        k: v
        for k, v in state.files.items()
        if k in old_files and v != old_files[k] or k not in old_files
    }

    check_result(
        list_files(old_files_filtered),
        list_files(new_files_filtered),
        prompt,
    )

    return state.files


def apply_prompt_to_directory(prompt: str, target_dir: str) -> None:
    files = {
        f: read_file(os.path.join(target_dir, f))
        for f in repo.get_all_checked_in_files(target_dir)
        if os.path.isfile(os.path.join(target_dir, f))
    }
    updated_files = apply_prompt_to_files(prompt, files)
    synchronize_files(target_dir, files, updated_files)


def process_directory(prompt: str, target_dir: str) -> None:
    apply_prompt_to_directory(prompt, target_dir)

    for iteration in range(3):
        pylint_result = run_pylint(os.path.join(target_dir, "src"))
        if pylint_result is not None and iteration < 2:
            # ask to fix pylint errors if we are in first or second iteration
            apply_prompt_to_directory(
                f"Fix these errors identified by PyLint:\n{pylint_result}", target_dir
            )
        elif pylint_result is not None and iteration == 2:
            # if errors are still present on the third iteration, raise an exception
            raise Exception("Pylint failed\n" + pylint_result)
        elif pylint_result is None:
            # if no pylint errors, break the loop
            break

    pytest_result = run_pytest(os.path.join(target_dir, "src"))
    if pytest_result is not None:
        raise Exception("Pytest failed\n" + pytest_result)


def process_issue(issue: Issue, dry_run: bool) -> None:
    if not repo.is_issue_open("reitzensteinm/duopoly", issue.number):
        return

    if CHECK_OPEN_PR and repo.check_issue_has_open_pr_with_same_title(
        "reitzensteinm/duopoly", issue.title
    ):
        return

    target_dir = f"target/issue-{issue.number}/duopoly"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    repo.clone_repository("https://github.com/reitzensteinm/duopoly.git", target_dir)

    branch_id = f"issue-{issue.id}"

    if not dry_run:
        repo.switch_and_reset_branch(branch_id, target_dir)

    process_directory(issue.description, target_dir)

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
