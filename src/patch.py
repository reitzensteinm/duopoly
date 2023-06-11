from utils import partition_by_predicate
import re


def patch_files(patch: str):
    # This is a hack - patches will be ignored if the file doesn't exist
    pattern = r"@@PATCH@@ (.+) (\d+) (\d+)"
    for l in patch.split("\n"):
        match = re.search(pattern, l)
        if match:
            yield match.group(1)


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
