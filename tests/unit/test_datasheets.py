import unittest

from robomind.domain import datasheets as D


class TestLookup(unittest.TestCase):
    def test_sg90_found(self):
        d = D.lookup("SG90")
        self.assertIsNotNone(d)
        self.assertEqual(d["type"], "servo")
        self.assertIn("torque_Nm", d)

    def test_case_insensitive(self):
        self.assertIsNotNone(D.lookup("sg90"))
        self.assertIsNotNone(D.lookup("MG996r"))

    def test_unknown(self):
        self.assertIsNone(D.lookup("NotARealPart42"))

    def test_category(self):
        self.assertEqual(D.category_of("SG90"), "servos")
        self.assertEqual(D.category_of("MPU6050"), "sensors")
        self.assertEqual(D.category_of("ESP32_DevKitC"), "mcus")


class TestSearch(unittest.TestCase):
    def test_search_substring(self):
        hits = D.search("MG")
        names = [n for n, _ in hits]
        self.assertIn("MG90S", names)
        self.assertIn("MG996R", names)

    def test_empty(self):
        self.assertEqual(D.search(""), [])

    def test_limit(self):
        hits = D.search("e", limit=2)
        self.assertLessEqual(len(hits), 2)


class TestInventory(unittest.TestCase):
    def test_all_names_non_empty(self):
        inv = D.all_names()
        for cat, names in inv.items():
            self.assertGreater(len(names), 0, f"empty category {cat}")

    def test_expected_categories(self):
        inv = D.all_names()
        for cat in ("servos", "motors", "mcus", "sensors", "batteries"):
            self.assertIn(cat, inv)

    def test_torque_values_consistent(self):
        # every servo should have both kgcm and Nm
        for name, sheet in D.SERVOS.items():
            self.assertIn("torque_kgcm", sheet, name)
            self.assertIn("torque_Nm", sheet, name)


if __name__ == "__main__":
    unittest.main()