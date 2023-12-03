import os
import uuid
import subprocess
import gpt
from utils import (
    read_file,
    write_file,
    add_line_numbers,
    list_files,
    synchronize_files_write,
)
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
from pipeline.project import Project
from repo import Issue
from tools.imports import imports
from tools.search import search_tool
from tools.pylint import run_pylint
from tools.pytest import run_pytest
from tools.advice import generate_advice
from utilities.prompts import load_prompt
from pipeline.issue_state import IssueState


class QualityException(Exception):
    """Exception raised when a quality check fails."""


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


def apply_prompt_to_files(prompt: str, files: dict, target_dir: str = None) -> dict:
    old_files = files
    advice = generate_advice(prompt)
    code_path = settings.CODE_PATH
    style = files.get("STYLE", "")
    context = {
        "files": ", ".join(files.keys()),
        "advice": advice,
        "goal": prompt,
        "code_path": code_path,
        "style": style,
    }
    prompt = load_prompt("issue", context)
    command, state = command_loop(
        prompt, gpt.SYSTEM_COMMAND_FUNC, COMMANDS_GENERATE, files, target_dir=target_dir
    )
    check_result(old_files, state.files, prompt)
    return state.files


def apply_prompt_to_directory(prompt: str, target_dir: str) -> None:
    files = {
        f: read_file(os.path.join(target_dir, f))
        for f in repo.list_files(target_dir, settings.GITIGNORE_PATH)
        if os.path.isfile(os.path.join(target_dir, f))
    }
    updated_files = apply_prompt_to_files(prompt, files, target_dir=target_dir)
    synchronize_files_write(target_dir, files, updated_files)


def process_directory(project: Project) -> None:
    """Processes the directory associated with the given Project instance.

    Raises a QualityException when either pylint or pytest fail.

    Args:
            project (Project): The project instance to process.

    Returns:
            None
    """
    settings_instance = settings.get_settings()
    if settings_instance.quality_checks:
        for iteration in range(settings.PYLINT_RETRIES + 1):
            pylint_result = run_pylint(os.path.join(project.path, "src"))
            if pylint_result is not None and iteration < settings.PYLINT_RETRIES:
                apply_prompt_to_directory(
                    f"Fix these errors identified by PyLint:\n{pylint_result}",
                    project.path,
                )
            elif pylint_result is not None and iteration == settings.PYLINT_RETRIES:
                raise QualityException("Pylint failed\n" + pylint_result)
            elif pylint_result is None:
                break
        pytest_result = run_pytest(os.path.join(project.path, "src"))
        if pytest_result is not None:
            raise QualityException("Pytest failed\n" + pytest_result)


def get_target_dir(issue: Issue) -> str:
    """Constructs the target directory path for the given issue."""
    return f"target/issue-{issue.number}/{issue.repository}"


def get_branch_id(issue: Issue) -> str:
    """Generates a unique branch identifier for the given issue."""
    return f"issue-{issue.id}"


def prepare_branch(issue: Issue, dry_run: bool) -> Project:
    """Sets up the local branch for processing an issue.

    Cloning and directory preparation are handled by the clone_repository function.

    Args:
            issue (Issue): The issue object containing details required to prepare the branch.
            dry_run (bool): Indicates whether the setup should be a dry run without actual changes.

    Returns:
            Project: A Project instance with path set to the location where the branch is set up.
    """
    branch_id = get_branch_id(issue)
    if not dry_run:
        target_dir = get_target_dir(issue)
        repo.clone_repository(issue.repository, target_dir)
        repo.switch_and_reset_branch(branch_id, target_dir)
    else:
        target_dir = os.path.join("dry_run", branch_id)
    return Project(path=target_dir)


def process_issue(issue: Issue, dry_run: bool) -> None:
    """Processes a single issue by setting up a branch, applying prompts, running checks, and creating PRs.

    This function handles quality checks, retry counts, open PR checks, and ensures processing
    only occurs for open issues and eligible authors.

    Args:
            issue (Issue): The issue to be processed.
            dry_run (bool): If true, avoids making actual changes to branches or files.

    Returns:
            None
    """
    is_quality_exception = False
    if issue.author not in settings.ADMIN_USERS:
        return
    if not repo.is_issue_open(issue.repository, issue.number):
        return
    settings_instance = settings.get_settings()
    if (
        settings_instance.check_open_pr
        and repo.check_issue_has_open_pr_with_same_title(issue.repository, issue.title)
    ):
        return
    issue_state = IssueState.retrieve_by_id(issue.id)
    formatted_prompt = f"Title: {issue.title}\nDescription: {issue.description}"
    if issue_state.prompt != formatted_prompt:
        issue_state.retry_count = 0
        issue_state.prompt = formatted_prompt
        issue_state.store()
    if issue_state.retry_count > settings_instance.max_issue_retries:
        return
    issue_state.retry_count += 1
    issue_state.store()
    try:
        process_directory(project=prepare_branch(issue, dry_run))
    except QualityException:
        is_quality_exception = True
    if not dry_run and not is_quality_exception:
        repo.commit_local_modifications(
            issue.title, f'Prompt: "{formatted_prompt}"', project_instance.path
        )
        repo.push_local_branch_to_origin(get_branch_id(issue), project_instance.path)
        if not repo.check_pull_request_title_exists(issue.repository, issue.title):
            repo.create_pull_request(
                issue.repository, get_branch_id(issue), issue.title, formatted_prompt
            )
