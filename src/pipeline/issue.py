import os
import uuid
import subprocess
import gpt
from utils import read_file, write_file, add_line_numbers, list_files, synchronize_files
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
)
from commands.loop import command_loop
import repo
import settings
import shutil
from repo import Issue
from tools.imports import imports
from tools.search import search_tool
from tools.pylint import run_pylint
from tools.pytest import run_pytest
from tools.advice import generate_advice
from utilities.prompts import load_prompt

CHECK_OPEN_PR = False


def check_result(old_files, new_files, prompt) -> bool:
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
    command, state = command_loop(
        f"""ORIGINAL:
{list_files(old_files_filtered)}
MODIFIED:
{list_files(new_files_filtered)}
OBJECTIVE:
{prompt}""",
        gpt.SYSTEM_CHECK_FUNC,
        COMMANDS_CHECK,
        new_files,
    )
    if not command.verdict:
        raise Exception("NEGATIVE VERDICT: " + command.reasoning)
    return command.verdict


def apply_prompt_to_files(prompt: str, files: dict) -> dict:
    old_files = files
    advice = generate_advice(prompt)
    context = {
        "files": ", ".join(files.keys()),
        "advice": advice,
        "goal": prompt,
        "details": "Imports should be relative to "
        + settings.CODE_PATH
        + ", so "
        + settings.CODE_PATH
        + "/cat/dog.py should be imported as 'cat.dog'",
    }
    prompt = load_prompt("issue", context)
    command, state = command_loop(
        prompt, gpt.SYSTEM_COMMAND_FUNC, COMMANDS_GENERATE, files
    )
    check_result(old_files, state.files, prompt)
    return state.files


def apply_prompt_to_directory(prompt: str, target_dir: str) -> None:
    files = {
        f: read_file(os.path.join(target_dir, f))
        for f in repo.list_files(target_dir, settings.GITIGNORE_PATH)
        if os.path.isfile(os.path.join(target_dir, f))
    }
    updated_files = apply_prompt_to_files(prompt, files)
    synchronize_files(target_dir, files, updated_files)


def process_directory(prompt: str, target_dir: str) -> None:
    apply_prompt_to_directory(prompt, target_dir)
    for iteration in range(3):
        pylint_result = run_pylint(os.path.join(target_dir, "src"))
        if pylint_result is not None and iteration < 2:
            apply_prompt_to_directory(
                f"Fix these errors identified by PyLint:\n{pylint_result}", target_dir
            )
        elif pylint_result is not None and iteration == 2:
            raise Exception("Pylint failed\n" + pylint_result)
        elif pylint_result is None:
            break
    pytest_result = run_pytest(os.path.join(target_dir, "src"))
    if pytest_result is not None:
        raise Exception("Pytest failed\n" + pytest_result)


def process_issue(issue: Issue, dry_run: bool) -> None:
    if not repo.is_issue_open(settings.REPOSITORY_PATH, issue.number):
        return
    if CHECK_OPEN_PR and repo.check_issue_has_open_pr_with_same_title(
        settings.REPOSITORY_PATH, issue.title
    ):
        return
    target_dir = f"target/issue-{issue.number}/{settings.REPOSITORY_PATH}"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir, exist_ok=True)
    repo.clone_repository(
        f"https://github.com/{settings.REPOSITORY_PATH}.git", target_dir
    )
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
            settings.REPOSITORY_PATH, issue.title
        ):
            repo.create_pull_request(
                repo_name=settings.REPOSITORY_PATH,
                branch_id=branch_id,
                title=issue.title,
                body=issue.description,
            )
