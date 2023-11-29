from typing import Dict, Optional
from utilities.cache import read, write


class IssueState:
    """Represents the state of an issue with a retry count and an associated prompt.

    Args:
            id (int): The identifier of the issue.

    Returns:
            IssueState: An instance representing the issue state.

    """

    initial_files: Optional[Dict[str, str]] = None
    """The initial files property is a dictionary mapping filename to file contents, with a default value of None.

	Args:
	        None

	Returns:
	        Optional[Dict[str, str]]: A mapping of filenames to file contents or None.

	"""

    def __init__(self, id: int):
        """Initialize the IssueState with an ID, a retry count set to zero, and an empty prompt.

        Args:
                id (int): The identifier of the issue.

        """
        self.id = id
        self.retry_count: int = 0
        self.prompt: str = ""

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
