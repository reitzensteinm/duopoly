import os
from github import Github
import openai


def partition_by_predicate(sequence, predicate):
    result = []
    current_group = []
    
    for item in sequence:
        if predicate(item):
            if current_group:
                result.append(current_group)
                current_group = []
            current_group.append(item)
        else:
            current_group.append(item)
            
    if current_group:
        result.append(current_group)
        
    return result


def gpt_query(message: str) -> str:
    """Queries GPT-4 with a given message."""
    openai.api_key = os.environ["OPENAI_API_KEY"]

    completion = openai.ChatCompletion.create(model="gpt-4", messages=[
        {"role": "system", "content": "You are a helpful programming assistant. \
        You will be given code as well as instructions to modify it. \
        Please make ONLY the changes requested, and respond only with code and no extra information or formatting \
        and follow PEP-8 formatting standards. Do not quote the output in markdown.\
        Unless specifically asked, do not ever delete, remove, replace, or modify any of the original file. \
        Your response should be as long as is needed to fit the resulting code in. \
        DO NOT DELETE ANY CODE YOU HAVE NOT BEEN ASKED TO!! \
        If asked to add a function, do not call it unless that was also asked for."},
        {"role": "user", "content": message}
    ])

    return completion.choices[0].message.content


def read_file(path: str) -> str:
    """Reads and returns the content of a file."""
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def write_file(path: str, contents: str) -> None:
    """Writes the contents to a file."""
    with open(path, 'w', encoding='utf-8') as file:
        file.write(contents)


def fetch_open_issues(repo_name: str) -> list:
    """Fetches open issues from a given repository."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state='open')
    descriptions = [issue.body for issue in issues]
    return descriptions


def add_line_numbers(file_contents: str) -> str:
    """Returns the file contents with line numbers added."""
    lines = file_contents.split('\n')
    numbered_lines = [f"{idx+1}: {line}" for idx, line in enumerate(lines)]
    return '\n'.join(numbered_lines)


def main() -> None:
    """Main function to handle program execution."""
    for prompt in fetch_open_issues("reitzensteinm/duopoly"):
        path = "main.py"
        write_file(path, gpt_query(f"{prompt}\n{read_file(path)}"))


if __name__ == '__main__':
    main()