from git import Repo
from datetime import datetime


def generate_statistics(repo_dir, time_range):
    """
    Generate statistics on the number of AI and human commits within a time range.

    Parameters:
    - repo_dir: The directory to the git repository.
    - time_range: A tuple containing two datetime objects (start, end) specifying the time range.

    Returns:
    A dict with the following keys:
    - 'ai': The count of AI-written commits.
    - 'human': The count of human-written commits.
    - 'ai_percentage': The percentage of commits written by AI.
    """
    ai_email = "133977416+duopoly@users.noreply.github.com"
    commit_counts = {"ai": 0, "human": 0, "ai_percentage": 0.0}

    # Open the repository
    repo = Repo(repo_dir)

    # Establish the time range for commits
    start_time, end_time = time_range

    # Fetch commits within the time range
    commits = list(repo.iter_commits(since=start_time, until=end_time))

    for commit in commits:
        # Check if the commit is written by the AI
        if commit.committer.email == ai_email:
            commit_counts["ai"] += 1
        else:
            commit_counts["human"] += 1

    total_commits = commit_counts["ai"] + commit_counts["human"]

    # Calculate the percentage of AI-written commits if there are any commits
    if total_commits > 0:
        commit_counts["ai_percentage"] = (commit_counts["ai"] / total_commits) * 100

    return commit_counts
