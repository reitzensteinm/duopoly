def commit_local_modifications(commit_name: str, commit_body: str):
    repo = Repo(os.getcwd())
    repo.git.add(update=True)
    repo.index.commit(commit_name + ": " + commit_body)
