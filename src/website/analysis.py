from git import Repo
from datetime import datetime, timedelta
import pprint


def print_analysis(repo_dir):
    pprinter = pprint.PrettyPrinter(indent=4)

    one_month_ago = datetime.now() - timedelta(days=30)
    three_months_ago = datetime.now() - timedelta(days=90)
    beginning_of_time = datetime.min

    # Last month statistics
    last_month_stats = generate_statistics(repo_dir, (one_month_ago, datetime.now()))
    print("Last month statistics:")
    pprinter.pprint(last_month_stats)

    # Last three months statistics
    last_three_months_stats = generate_statistics(
        repo_dir, (three_months_ago, datetime.now())
    )
    print("Last three months statistics:")
    pprinter.pprint(last_three_months_stats)

    # All-time statistics
    all_time_stats = generate_statistics(repo_dir, (beginning_of_time, datetime.now()))
    print("All-time statistics:")
    pprinter.pprint(all_time_stats)


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
    - 'last_human_commit_date': The date of the last human commit.
    """
    ai_email = "133977416+duopoly@users.noreply.github.com"
    commit_counts = {
        "ai": 0,
        "human": 0,
        "ai_percentage": 0.0,
        "last_human_commit_date": None,
    }

    # Open the repository
    repo = Repo(repo_dir)

    # Establish the time range for commits
    start_time, end_time = time_range

    # Fetch commits within the time range
    commits = list(repo.iter_commits(since=start_time, until=end_time))

    last_human_commit_date = None
    for commit in commits:
        # Check if the commit is written by the AI
        if commit.committer.email == ai_email:
            commit_counts["ai"] += 1
        else:
            commit_counts["human"] += 1
            last_human_commit_date = commit.committed_datetime

    total_commits = commit_counts["ai"] + commit_counts["human"]

    # Calculate the percentage of AI-written commits if there are any commits
    if total_commits > 0:
        commit_counts["ai_percentage"] = (commit_counts["ai"] / total_commits) * 100

    # Set the date of the last human commit
    if last_human_commit_date:
        commit_counts["last_human_commit_date"] = last_human_commit_date

    return commit_counts
