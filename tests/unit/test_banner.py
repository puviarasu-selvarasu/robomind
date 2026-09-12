import unittest
from robomind.ui.banner import compact, wordmark


class TestBanner(unittest.TestCase):
    def test_compact_single_line(self):
        s = compact("0.1.0")
        self.assertIn("ROBOMIND", s)
        self.assertIn("0.1.0", s)
        self.assertEqual(s.count("\n"), 0)

    def test_wordmark_has_multiple_rows(self):
        rows = wordmark()
        self.assertGreaterEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()