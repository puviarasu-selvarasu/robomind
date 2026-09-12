import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from robomind.config import build_config


class TestConfig(unittest.TestCase):
    def test_defaults_with_cli_home(self):
        with TemporaryDirectory() as td:
            home = Path(td) / "rm"
            cfg = build_config({"home": str(home)})
            self.assertEqual(cfg.home, home)
            self.assertEqual(cfg.db, home / "robomind.db")
            self.assertEqual(cfg.log_dir, home / "logs")
            self.assertEqual(cfg.voice, "off")
            self.assertEqual(cfg.face, "off")
            self.assertEqual(cfg.llm, "off")
            self.assertTrue(home.exists())

    def test_validate_clean(self):
        with TemporaryDirectory() as td:
            cfg = build_config({"home": td})
            self.assertEqual(cfg.validate(), [])

    def test_validate_rejects_bad_face_size(self):
        with TemporaryDirectory() as td:
            cfg = build_config({"home": td, "face_size": "not-a-size"})
            self.assertTrue(any("face_size" in e for e in cfg.validate()))

    def test_env_override(self):
        with TemporaryDirectory() as td:
            with patch.dict(os.environ, {"ROBOMIND_VOICE": "on"}, clear=False):
                cfg = build_config({"home": td})
                self.assertEqual(cfg.voice, "on")

    def test_cli_beats_env(self):
        with TemporaryDirectory() as td:
            with patch.dict(os.environ, {"ROBOMIND_VOICE": "on"}, clear=False):
                cfg = build_config({"home": td, "voice": "off"})
                self.assertEqual(cfg.voice, "off")

    def test_json_config_loaded(self):
        with TemporaryDirectory() as td:
            home = Path(td)
            (home / "config.json").write_text('{"voice": "on"}', encoding="utf-8")
            cfg = build_config({"home": str(home)})
            self.assertEqual(cfg.voice, "on")


if __name__ == "__main__":
    unittest.main()