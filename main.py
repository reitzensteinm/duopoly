import os
from github import Github
import openai
import re
from black import FileMode, format_str
import fnmatch
from utils import read_file, write_file


def format_python_code(code: str) -> str:
    formatted_code = format_str(code, mode=FileMode())
    return formatted_code


def find_python_files() -> list[str]:
    python_files = []

    for root, dirnames, filenames in os.walk("."):
        for filename in fnmatch.filter(filenames, "*.py"):
            if "venv" not in root:
                python_files.append(os.path.join(root, filename))

    return python_files


from utils import read_file, write_file, partition_by_predicate


def gpt_query(message: str) -> str:
    """Sends a message to GPT-4 and returns the response."""
    openai.api_key = os.environ["OPENAI_API_KEY"]

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful programming assistant. \
        You will be given code as well as instructions to modify it. \
        Please make ONLY the changes requested, and respond only with the changes in the format specified \
        and follow PEP-8 formatting standards. \
        The format for the patch should contain one line with start and end lines of the original file to replace, \
        followed by the new lines. Do not include the line numbers from the input. \
        Do not include any unnecessary blank lines in the patches. \
        RESPOND ONLY IN THE FOLLOWING FORMAT, AND DO NOT INCLUDE ANY OTHER COMMENTARY: \
        @@PATCH@@ <file name including relative path> <start-line> <end-line> \
        <new line 1>\
        <new line 2> ...",
            },
            {"role": "user", "content": message},
        ],
    )

    return completion.choices[0].message.content


def fetch_open_issues(repo_name: str) -> list[str]:
    """Fetches open issues from a given repository."""
    api_key = os.environ["GITHUB_API_KEY"]
    g = Github(api_key)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="open")
    descriptions = [issue.body for issue in issues]
    return descriptions


def add_line_numbers(file_contents: str) -> str:
    """Returns the file contents with line numbers added."""
    lines = file_contents.split("\n")
    numbered_lines = [f"{idx+1}: {line}" for idx, line in enumerate(lines)]
    return "\n".join(numbered_lines)


def patch_prepass(patch: str):
    # This is a hack - patches will be ignored if the file doesn't exist
    pattern = r"@@PATCH@@ (.+) (\d+) (\d+)"
    for l in patch.split("\n"):
        match = re.search(pattern, l)
        if match:
            file = match.group(1)
            if not os.path.exists(file):
                write_file(file, "")


def apply_patch(file_name: str, file: str, patch: str) -> str:
    """Applies the given patch to the file contents."""
    pattern = r"@@PATCH@@ (.+) (\d+) (\d+)"

    def apply_patch_inner(file_lines, patch_lines, off):
        match = re.search(pattern, patch_lines[0])
        patch_file = match.group(1)

        if patch_file != file_name:
            return off, file_lines

        start = int(match.group(2)) + off
        end = int(match.group(3)) + off
        off = off + ((len(patch_lines) - 1) - (1 + end - start))
        return off, file_lines[0 : start - 1] + patch_lines[1:] + file_lines[end:]

    file_lines = file.split("\n")
    patch_lines = patch.split("\n")
    offset = 0

    patches = partition_by_predicate(patch_lines, lambda l: re.search(pattern, l))
    patches.sort(key=lambda p: int(re.search(pattern, p[0]).group(2)))

    for p in patches:
        offset, file_lines = apply_patch_inner(file_lines, p, offset)

    return "\n".join(file_lines)


def main() -> None:
    """Main function to handle program execution."""
    for prompt in fetch_open_issues("reitzensteinm/duopoly"):
        file_info = ""
        for f in find_python_files():
            file_info += f"{f}:\n{add_line_numbers(read_file(f))}\n"

        patch = gpt_query(f"{prompt}\n{file_info}")
        patch_prepass(patch)
        print(patch)

        for f in find_python_files():
            write_file(f, format_python_code(apply_patch(f, read_file(f), patch)))


if __name__ == "__main__":
    main()
