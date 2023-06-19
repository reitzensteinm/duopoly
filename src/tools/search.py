def search_tool(files: dict, search_string: str) -> list:
    matching_files = [
        filename for filename, content in files.items() if search_string in content
    ]
    return matching_files
