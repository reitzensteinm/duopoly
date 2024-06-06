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


def apply_prompt_to_files(prompt: str, files: dict, project: Project = None) -> dict:
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
        prompt,
        gpt.SYSTEM_COMMAND_FUNC,
        COMMANDS_GENERATE,
        files,
        target_dir=project.path if project else None,
    )
    check_result(old_files, state.files, prompt)
    return state.files


def apply_prompt_to_directory(prompt: str, project: Project) -> None:
    files = {
        f: read_file(os.path.join(project.path, f))
        for f in repo.list_files(project.path, settings.GITIGNORE_PATH)
        if os.path.isfile(os.path.join(project.path, f))
    }
    updated_files = apply_prompt_to_files(prompt, files, project=project)
    synchronize_files_write(project.path, files, updated_files)


def process_directory(prompt: str, project: Project) -> None:
    """Processes the directory of the specified Project with the provided prompt and conducts quality checks using pylint and pytest.

    Raises a QualityException if pylint or pytest fails after retry limits.

    Params:
    prompt (str): The prompt describing the processing task.
    project (Project): The Project instance to be processed.

    """
    apply_prompt_to_directory(prompt, project)
    settings_instance = settings.get_settings()
    if settings_instance.quality_checks:
        for iteration in range(PYLINT_RETRIES + 1):
            pylint_result = run_pylint(os.path.join(project.path, "src"))
            if pylint_result is not None and iteration < PYLINT_RETRIES:
                apply_prompt_to_directory(
                    f"Fix these errors identified by PyLint:\n{pylint_result}",
                    project,
                )
            elif pylint_result is not None and iteration == PYLINT_RETRIES:
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

    Params:
                    issue (Issue): The issue object containing details required to prepare the branch.
                    dry_run (bool): Indicates whether the branch setup should actually be performed or not.

    Returns:
                    Project: A Project instance with path set to the location where the branch is set up.
    """
    target_dir = get_target_dir(issue)
    repo.clone_repository(
        f"https://{os.environ['GITHUB_API_KEY']}@github.com/{issue.repository}.git",
        target_dir,
    )
    branch_id = get_branch_id(issue)
    if not dry_run:
        repo.switch_and_reset_branch(branch_id, target_dir)
    return Project(path=target_dir)


def process_issue(issue: Issue, dry_run: bool) -> None:
    """Processes a single issue by setting up a branch, applying prompts, running checks, and creating pull requests.

    The function checks the retry count, and skips processing if max retries are exceeded, if the author is not an admin, the issue is not open, or if there is an open PR for the issue.

    Params:
                    issue (Issue): The issue to be processed.
                    dry_run (bool): If true, no writes or branch modifications are conducted.

    Returns:
                    None
    """
    is_quality_exception = False
    if issue.author not in settings.get_settings().admin_users:
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
        print(
            f"\x1b[91mSkipping processing of issue {issue.number} due to too many attempts\x1b[0m"
        )
        return
    issue_state.retry_count += 1
    issue_state.store()
    project_instance = prepare_branch(issue, dry_run)
    try:
        process_directory(formatted_prompt, project_instance)
    except QualityException:
        is_quality_exception = True
    if not dry_run:
        repo.commit_local_modifications(
            issue.title, f'Prompt: "{formatted_prompt}"', project_instance.path
        )
        repo.push_local_branch_to_origin(get_branch_id(issue), project_instance.path)
        if not repo.check_pull_request_title_exists(issue.repository, issue.title):
            if is_quality_exception and settings_instance.quality_checks:
                repo.create_pull_request(
                    repo_name=issue.repository,
                    branch_id=get_branch_id(issue),
                    title=issue.title,
                    body="This PR addresses issue #"
                    + str(issue.number)
                    + ". "
                    + formatted_prompt,
                    draft=True,
                )
            else:
                repo.create_pull_request(
                    repo_name=issue.repository,
                    branch_id=get_branch_id(issue),
                    title=issue.title,
                    body="This PR addresses issue #"
                    + str(issue.number)
                    + ". "
                    + formatted_prompt,
                )
