import unittest
import os
from trace import Trace


class TestTrace(unittest.TestCase):

    def setUp(self) -> None:
        self.trace = Trace("test_trace")
        self.trace_file = f"traces/{self.trace.name}.html"
        if not os.path.exists("traces"):
            os.mkdir("traces")

    def test_add_trace_data_utf8_encoding(self) -> None:
        """Test that add_trace_data writes a trace with UTF-8 encoding."""
        test_html_content = "<div>Test Trace Content</div>"
        self.trace.add_trace_data("test_tag", test_html_content)

        self.assertTrue(os.path.exists(self.trace_file))

        with open(self.trace_file, "rb") as file:
            content_bytes = file.read()

        try:
            content = content_bytes.decode("utf-8")
            self.assertEqual(content, test_html_content)
        except UnicodeDecodeError:
            self.fail("The trace file is not encoded with UTF-8")

    def tearDown(self) -> None:
        if os.path.exists(self.trace_file):
            os.remove(self.trace_file)
        if os.path.exists("traces"):
            os.rmdir("traces")


if __name__ == "__main__":
    unittest.main()
