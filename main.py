import os
from github import Github
import openai
import re
from black import FileMode, format_str

def format_python_code(code: str) -> str:
    formatted_code = format_str(code, mode=FileMode())
    return formatted_code
import fnmatch

def find_python_files() -> list[str]:
    python_files = []

    for root, dirnames, filenames in os.walk('.'):
        for filename in fnmatch.filter(filenames, '*.py'):
            python_files.append(os.path.join(root, filename))

    return python_files
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
        Please make ONLY the changes requested, and respond only with the changes in the format specified \
        and follow PEP-8 formatting standards. \
        The format for the patch should contain one line with start and end lines of the original file to replace, \
        followed by the new lines. Do not include the line numbers from the input. \
        Do not include any unnecessary blank lines in the patches. \
        @@PATCH@@ <start-line> <end-line> \
        <new line 1>\
        <new line 2> ..."},
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


def apply_patch(file, patch):
    pattern = r"@@PATCH@@ (\d+) (\d+)"

    def apply_patch_inner(file_lines, patch_lines, off):
        match = re.search(pattern, patch_lines[0])
        start = int(match.group(1)) + off
        end = int(match.group(2)) + off
        off = off + ((len(patch_lines) - 1) - (1 + end - start))
        return off, file_lines[0:start - 1] + patch_lines[1:] + file_lines[end:]

    file_lines = file.split('\n')
    patch_lines = patch.split('\n')
    offset = 0

    patches = partition_by_predicate(patch_lines, lambda l: re.search(pattern, l))

    for p in patches:
        offset, file_lines = apply_patch_inner(file_lines, p, offset)

    return "\n".join(file_lines)


def main() -> None:
    """Main function to handle program execution."""
    for prompt in fetch_open_issues("reitzensteinm/duopoly"):
        path = "main.py"
        patch = gpt_query(f"{prompt}\n{add_line_numbers(read_file(path))}")
        print(patch)
        write_file(path, apply_patch(read_file(path), patch))


if __name__ == '__main__':
    main()