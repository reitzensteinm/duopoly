import json


def parse_coverage_json(coverage_json):
    """
    Parse JSON data from a pytest coverage export.

    Arguments:
    coverage_json: A JSON string or dictionary containing pytest coverage data.

    Returns:
    A dictionary mapping file paths to coverage percentages.
    """
    if isinstance(coverage_json, str):
        coverage_data = json.loads(coverage_json)
    else:
        coverage_data = coverage_json

    coverage_mapping = {}
    for file_path, coverage_info in coverage_data["files"].items():
        coverage_summary = coverage_info["summary"]
        total_lines = coverage_summary["num_statements"]
        covered_lines = coverage_summary["covered_statements"]
        if total_lines > 0:
            coverage_percent = (covered_lines / total_lines) * 100
        else:
            coverage_percent = (
                100  # Assuming if there are no statements, it's 100% covered
            )
        coverage_mapping[file_path] = coverage_percent

    return coverage_mapping
