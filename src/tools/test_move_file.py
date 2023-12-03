import unittest
from unittest.mock import patch, MagicMock
from tools.move_file import move_file_using_rope


class TestMoveFile(unittest.TestCase):
    """Tests for the move_file.py module."""

    @patch("tools.move_file.Project")
    def test_move_file_using_rope_success(self, MockProject):
        """Test move_file_using_rope function moves a file successfully when given valid paths.

        Project mock simulates a rope project. Check if file move is called correctly.
        """
        mock_project_instance = MockProject.return_value
        mock_project_instance.get_file.return_value = MagicMock()
        mock_project_instance.get_folder.return_value = MagicMock()

        # Perform the file move
        move_file_using_rope(
            "project_directory", "relative/from/path.py", "relative/to/path.py"
        )

        mock_project_instance.get_file.assert_called_with("relative/from/path.py")
        mock_project_instance.get_folder.assert_called_with("relative/to/path.py")
        mock_project_instance.close.assert_called_once()

    @patch("tools.move_file.Project")
    def test_move_file_using_rope_source_file_not_found(self, MockProject):
        """Test move_file_using_rope function raises FileNotFoundError when source file is not found.

        Project mock simulates a rope project. Asserts FileNotFoundError is raised.
        """
        mock_project_instance = MockProject.return_value
        mock_project_instance.get_file.side_effect = FileNotFoundError

        with self.assertRaises(FileNotFoundError):
            move_file_using_rope(
                "project_directory",
                "relative/from/nonexistent.py",
                "relative/to/path.py",
            )

        mock_project_instance.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
