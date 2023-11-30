from utilities.cache import read, write
from typing import Optional, Dict


class IssueState:
    """Represents the state of an issue with a retry count, an associated prompt, a record of initial file states, and an optional PR ID.

    Args:
            id (int): The identifier of the issue.

    Returns:
            IssueState: An instance representing the issue state.

    Attributes:
            initial_files (Optional[Dict[str, str]]): A mapping of filenames to their contents representing initial file states, or None if there are no initial files.
            pr_id (Optional[int]): The identifier of the associated pull request, if any.
    """

    def __init__(self, id: int):
        """Initialize the IssueState with an ID, a retry count set to zero, an empty prompt, no initial files, and no associated PR ID.

        Args:
                id (int): The identifier of the issue.

        """
        self.id = id
        self.retry_count: int = 0
        self.prompt: str = ""
        self.initial_files: Optional[Dict[str, str]] = None
        self.pr_id: Optional[int] = None

    @staticmethod
    def retrieve_by_id(id: int) -> "IssueState":
        """Retrieve the issue state by id directly if it exists, or create and store a new one if not found.

        Args:
                id (int): The identifier of the issue.

        Returns:
                IssueState: The retrieved or newly created issue state.
        """
        try:
            return read(f"issue-{id}")
        except FileNotFoundError:
            new_issue = IssueState(id)
            write(f"issue-{id}", new_issue)
            return new_issue

    def store(self) -> None:
        """Store the current issue state.

        Returns:
                None
        """
        write(f"issue-{self.id}", self)

    def __str__(self) -> str:
        """Return a string representation of the issue state.

        Returns:
                str: The string representation of the issue state.
        """
        return str(self.__dict__)
