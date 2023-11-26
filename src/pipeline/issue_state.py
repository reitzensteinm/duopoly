from utilities.cache import read, write


class IssueState:
    """Represents the state of an issue with a retry count.

    Args:
            id (int): The identifier of the issue.

    """

    def __init__(self, id: int):
        """Initialize the IssueState with an ID and a retry count set to zero.

        Args:
                id (int): The identifier of the issue.

        """
        self.id = id
        self.retry_count: int = 0  # Initialize the retry count.

    @staticmethod
    def retrieve_by_id(id: int) -> "IssueState":
        try:
            issue_dict = read(f"issue-{id}.json")
            new_issue = IssueState(id)
            new_issue.__dict__.update(issue_dict)
            return new_issue
        except FileNotFoundError:
            new_issue = IssueState(id)
            write(f"issue-{id}.json", new_issue)
            return new_issue

    def store(self) -> None:
        write(f"issue-{self.id}.json", self)

    def __dict__(self) -> dict:
        return self.__dict__.copy()

    def __str__(self) -> str:
        return str(self.__dict__)
