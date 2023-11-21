import json
import pytest
from utilities.coverage import parse_coverage_json


def test_parse_valid_json_string():
    coverage_json = json.dumps(
        {
            "files": {
                "src/module/file.py": {
                    "summary": {"num_statements": 10, "covered_statements": 8}
                }
            }
        }
    )
    expected_result = {"src/module/file.py": 80.0}
    assert parse_coverage_json(coverage_json) == expected_result


def test_parse_valid_json_dict():
    coverage_data = {
        "files": {
            "src/module/file.py": {
                "summary": {"num_statements": 10, "covered_statements": 8}
            }
        }
    }
    expected_result = {"src/module/file.py": 80.0}
    assert parse_coverage_json(coverage_data) == expected_result


def test_parse_zero_total_lines():
    coverage_data = {
        "files": {
            "src/module/file.py": {
                "summary": {"num_statements": 0, "covered_statements": 0}
            }
        }
    }
    expected_result = {"src/module/file.py": 100.0}
    assert parse_coverage_json(coverage_data) == expected_result


def test_parse_malformed_json():
    malformed_json = '{"files": {"src/module/file.py": {"summary": { "num_statements": 10, }}}'  # Missing 'covered_statements' key
    with pytest.raises(json.JSONDecodeError):
        parse_coverage_json(malformed_json)
