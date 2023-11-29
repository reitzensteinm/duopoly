import unittest
from unittest.mock import patch, MagicMock
from repo import get_open_pr_comments, IssueComment


class TestRepo(unittest.TestCase):
    @patch("repo.Github")
    def test_get_open_pr_comments(self, mock_github):
        # Create a mock API response
        mock_comment = MagicMock()
        mock_comment.user.login = "username"
        mock_comment.body = "comment body"
        mock_pull = MagicMock()
        mock_pull.get_comments.return_value = [mock_comment]

        # Mock the Github repository and get_pulls method
        mock_repo = mock_github.return_value.get_repo.return_value
        mock_repo.get_pulls.return_value = [mock_pull]

        # Execute the function with the mock objects
        result = get_open_pr_comments("test/repo")

        # Assertions
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(comment, IssueComment) for comment in result))
        for comment in result:
            self.assertEqual(comment.username, "username")
            self.assertEqual(comment.content, "comment body")


if __name__ == "__main__":
    unittest.main()
