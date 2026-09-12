import unittest
from robomind.ui import ansi


class TestAnsi(unittest.TestCase):
    def test_strip(self):
        s = f"{ansi.FG_CYAN}hello{ansi.RESET}"
        self.assertEqual(ansi.strip_ansi(s), "hello")

    def test_visible_len(self):
        s = f"{ansi.BOLD}abc{ansi.RESET}de"
        self.assertEqual(ansi.visible_len(s), 5)

    def test_constants(self):
        self.assertTrue(ansi.RESET.startswith("\x1b["))
        self.assertTrue(ansi.FG_CYAN.startswith("\x1b["))


if __name__ == "__main__":
    unittest.main()