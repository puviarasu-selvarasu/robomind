import unittest
from robomind.core.ports import LLM, Renderer, Voice
from robomind.llm.null_llm import NullLLM
from robomind.ui.plain import PlainRenderer
from robomind.ui.voice.null_voice import NullVoice


class TestPorts(unittest.TestCase):
    def test_null_llm_satisfies(self):
        self.assertIsInstance(NullLLM(), LLM)

    def test_null_voice_satisfies(self):
        self.assertIsInstance(NullVoice(), Voice)

    def test_plain_renderer_satisfies(self):
        self.assertIsInstance(PlainRenderer(), Renderer)


if __name__ == "__main__":
    unittest.main()