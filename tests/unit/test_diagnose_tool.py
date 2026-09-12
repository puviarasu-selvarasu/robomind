import unittest
from robomind.tools.diagnose_tool import DiagnoseTool, diagnose


class TestDiagnose(unittest.TestCase):
    def test_servo_jitter(self):
        hits = diagnose("my servo is jittering when it moves")
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0][0].id, "servo.jitter")

    def test_mcu_reset(self):
        hits = diagnose("mcu keeps resetting when the motors start")
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0][0].id, "power.brownout")

    def test_no_match(self):
        hits = diagnose("the weather is nice today")
        self.assertEqual(hits, [])


class TestDiagnoseTool(unittest.TestCase):
    def setUp(self):
        self.tool = DiagnoseTool()

    def test_ok(self):
        r = self.tool.run(symptom="servo jitter")
        self.assertTrue(r.ok)
        self.assertGreater(len(r.value["matches"]), 0)

    def test_empty(self):
        r = self.tool.run(symptom="")
        self.assertFalse(r.ok)

    def test_no_match(self):
        r = self.tool.run(symptom="weather is nice")
        self.assertTrue(r.ok)
        self.assertEqual(r.value["matches"], [])


if __name__ == "__main__":
    unittest.main()