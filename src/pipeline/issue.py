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
from settings import PYLINT_RETRIES
import shutil
from repo import Issue
from tools.imports import imports
from tools.search import search_tool
from tools.pylint import run_pylint
from tools.pytest import run_pytest
from tools.advice import generate_advice
from utilities.prompts import load_prompt
from pipeline.issue_state import IssueState


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
    if settings.DO_QUALITY_CHECKS:
        for iteration in range(settings.PYLINT_RETRIES + 1):
            pylint_result = run_pylint(os.path.join(target_dir, "src"))
            if pylint_result is not None and iteration < settings.PYLINT_RETRIES:
                apply_prompt_to_directory(
                    f"Fix these errors identified by PyLint:\n{pylint_result}",
                    target_dir,
                )
            elif pylint_result is not None and iteration == settings.PYLINT_RETRIES:
                raise Exception("Pylint failed\n" + pylint_result)
            elif pylint_result is None:
                break
        pytest_result = run_pytest(os.path.join(target_dir, "src"))
        if pytest_result is not None:
            raise Exception("Pytest failed\n" + pytest_result)


def get_target_dir(issue):
    return f"target/issue-{issue.number}/{issue.repository}"


def get_branch_id(issue):
    return f"issue-{issue.id}"


def prepare_branch(issue: Issue, dry_run: bool) -> None:
    target_dir = get_target_dir(issue)
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir, exist_ok=True)
    repo.clone_repository(
        f"https://{os.environ['GITHUB_API_KEY']}@github.com/{issue.repository}.git",
        target_dir,
    )
    branch_id = get_branch_id(issue)
    if not dry_run:
        repo.switch_and_reset_branch(branch_id, target_dir)
    return target_dir


def process_issue(issue: Issue, dry_run: bool) -> None:
    if issue.author not in settings.ADMIN_USERS:
        return
    if not repo.is_issue_open(issue.repository, issue.number):
        return
    if settings.CHECK_OPEN_PR and repo.check_issue_has_open_pr_with_same_title(
        issue.repository, issue.title
    ):
        return
    target_dir = prepare_branch(issue, dry_run)
    formatted_prompt = f"Title: {issue.title}\nDescription: {issue.description}"
    process_directory(formatted_prompt, target_dir)
    issue_state = IssueState(issue.id)
    if not dry_run:
        repo.commit_local_modifications(
            issue.title, f'Prompt: "{formatted_prompt}"', target_dir
        )
        repo.push_local_branch_to_origin(get_branch_id(issue), target_dir)
        if not repo.check_pull_request_title_exists(issue.repository, issue.title):
            repo.create_pull_request(
                repo_name=issue.repository,
                branch_id=get_branch_id(issue),
                title=issue.title,
                body="This PR addresses issue #"
                + str(issue.number)
                + ". "
                + formatted_prompt,
            )
