import yaml
from typing import Any, Dict, Optional

from .issue_state import IssueState
from .project import Project
from settings import Settings, get_settings
from repo import (
    list_files,
    clone_repository,
    switch_and_reset_branch,
    is_issue_open,
    check_issue_has_open_pr_with_same_title,
    is_admin_user,
    create_pull_request,
    commit_local_modifications,
    push_local_branch_to_origin,
    check_pull_request_title_exists,
)


class Issue:
    def __init__(
        self,
        number: int,
        title: str,
        description: str,
        repository: str,
        author: str,
        id: Optional[int] = None,
    ) -> None:
        self.number: int = number
        self.title: str = title
        self.description: str = description
        self.repository: str = repository
        self.author: str = author
        self.id: int = id if id is not None else self.number

    def process(self, settings: Settings, dry_run: bool = False) -> None:
        if not is_issue_open(self.repository, self.number) or (
            get_settings().check_open_pr
            and check_issue_has_open_pr_with_same_title(self.repository, self.title)
        ):
            return

        if not is_admin_user(self.author):
            return

        issue_state: IssueState = IssueState.retrieve_by_id(self.id)
        formatted_prompt: str = f"Title: {self.title}\nDescription: {self.description}"

        if issue_state.prompt != formatted_prompt:
            issue_state.reset_state(formatted_prompt)

        if issue_state.should_skip_due_to_retries(settings.max_issue_retries):
            issue_state.log_skip(self.number)
            return

        issue_state.increment_retry_count()
        project: Project = self.setup_local_branch(dry_run)

        apply_settings_to_project(project.path)

        try:
            project.process_directory(formatted_prompt, committee=settings.committee)
        except QualityException as e:
            self.handle_quality_exception(e, project.path, formatted_prompt, dry_run)

        # Push the changes and create a pull request if needed
        project.wrap_up_issue(self, dry_run)

    def setup_local_branch(self, dry_run: bool) -> Project:
        target_dir: str = self.get_target_dir()
        clone_repository(self.repository, target_dir)
        branch_id: str = self.get_branch_id()
        if not dry_run:
            switch_and_reset_branch(branch_id, target_dir)
        return Project(path=target_dir)

    def get_target_dir(self) -> str:
        return f"target/issue-{self.number}/{self.repository}"

    def get_branch_id(self) -> str:
        return f"issue-{self.id if self.id else self.number}"

    def handle_quality_exception(
        self,
        exception: Exception,
        target_dir: str,
        formatted_prompt: str,
        dry_run: bool,
    ) -> None:
        if not dry_run:
            commit_local_modifications(
                self.title, f'Prompt: "{formatted_prompt}"', target_dir
            )
            push_local_branch_to_origin(self.get_branch_id(), target_dir)
            if not check_pull_request_title_exists(self.repository, self.title):
                create_pull_request(
                    repo_name=self.repository,
                    branch_id=self.get_branch_id(),
                    title=self.title,
                    body=f"This PR addresses issue #{self.number}. {formatted_prompt}",
                    draft=True,
                )


def apply_settings_to_project(project_path: str) -> None:
    settings_path: str = f"{project_path}/duopoly.yaml"
    if yaml.safe_load(open(settings_path)) is not None:
        get_settings().load_from_yaml(settings_path)
