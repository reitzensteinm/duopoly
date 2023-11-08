def search_tool(files: dict, search_string: str) -> list:
    search_string = search_string.lower()
    matching_files = [
        filename
        for filename, content in files.items()
        if search_string in content.lower()
    ]
    return matching_files
