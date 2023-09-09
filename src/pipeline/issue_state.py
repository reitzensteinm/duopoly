from utilities.cache import read, write


class IssueState:
    def __init__(self, id):
        self.id = id

    @staticmethod
    def retrieve_by_id(id):
        try:
            return read(f"issue-{id}.json")
        except FileNotFoundError:
            new_issue = IssueState(id)
            write(f"issue-{id}.json", new_issue)
            return new_issue

    def store(self):
        write(f"issue-{self.id}.json", self)

    def __dict__(self):
        return self.__dict__.copy()

    def __str__(self):
        return str(self.__dict__)
