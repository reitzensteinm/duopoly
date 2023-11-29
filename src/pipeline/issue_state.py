from typing import Optional, Dict
from utilities.cache import read, write


class IssueState:
    """Represents the state of an issue with a retry count and an associated prompt.

    Args:
                    id (int): The identifier of the issue.
                    initial_files (Optional[Dict[str, str]]): A dictionary mapping filenames to their contents, defaults to None if not provided.

    Returns:
                    IssueState: An instance representing the issue state with the given id and initial_files.

    """

    def __init__(self, id: int, initial_files: Optional[Dict[str, str]] = None):
        """Initialize the IssueState with an ID, a retry count set to zero, an empty prompt, and initial files mapping.

        Args:
                        id (int): The identifier of the issue.
                        initial_files (Optional[Dict[str, str]]): A dictionary mapping filenames to their contents, defaults to None if not provided.

        """
        self.id = id
        self.retry_count: int = 0
        self.prompt: str = ""
        self.initial_files: Optional[Dict[str, str]] = initial_files

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
