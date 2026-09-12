import unittest
from robomind.ui import ansi
from robomind.ui.boxes import Box, render


class TestBoxes(unittest.TestCase):
    def test_basic_box(self):
        out = render(Box(title="hi", lines=["a", "b"], width=20))
        plain = ansi.strip_ansi(out)
        self.assertIn("hi", plain)
        self.assertIn("a", plain)
        self.assertIn("b", plain)
        self.assertIn("┌", plain)
        self.assertIn("└", plain)

    def test_wrap(self):
        out = render(Box(lines=["a " * 40], width=20))
        plain = ansi.strip_ansi(out)
        self.assertGreater(plain.count("\n"), 2)


if __name__ == "__main__":
    unittest.main()