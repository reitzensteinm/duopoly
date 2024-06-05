import unittest
from settings import Settings


class TestSettings(unittest.TestCase):
    """Tests for default values in the Settings class."""

    def setUp(self) -> None:
        """Set up test conditions."""
        self.settings = Settings()

    def test_use_tools_default_value(self) -> None:
        """Test that the default value for use_tools is True."""
        self.assertTrue(self.settings.use_tools)

    def test_max_workers_default_value(self) -> None:
        """Test that the default value for max_workers is 10."""
        self.assertEqual(self.settings.max_workers, 10)

    def test_max_input_chars_default_value(self) -> None:
        """Test that the default value for max_input_chars is 48000."""
        self.assertEqual(self.settings.max_input_chars, 48000)

    def test_quality_checks_default_value(self) -> None:
        """Test that the default value for quality_checks is True."""
        self.assertTrue(self.settings.quality_checks)

    def test_max_issue_retries_default_value(self) -> None:
        """Test that the default value for max_issue_retries is 2."""
        self.assertEqual(self.settings.max_issue_retries, 2)

    def test_max_loop_length_default_value(self) -> None:
        """Test that the default value for max_loop_length is 15."""
        self.assertEqual(self.settings.max_loop_length, 15)

    def test_check_open_pr_default_value(self) -> None:
        """Test that the default value for check_open_pr is True."""
        self.assertTrue(self.settings.check_open_pr)

    def tearDown(self) -> None:
        """Tear down test conditions."""
        del self.settings


if __name__ == "__main__":
    unittest.main()
