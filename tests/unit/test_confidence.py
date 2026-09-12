import unittest
from datetime import datetime, timedelta, timezone

from robomind.core import confidence as C


class TestConfidence(unittest.TestCase):
    def test_laplace_neutral(self):
        self.assertAlmostEqual(C.laplace_weight(0, 0), 0.5)

    def test_laplace_all_wins(self):
        self.assertGreater(C.laplace_weight(10, 10), C.laplace_weight(10, 5))

    def test_decay_weight_floor(self):
        w = 1.0
        for _ in range(1000):
            w = C.decay_weight(w, factor=0.99, floor=0.1)
        self.assertGreaterEqual(w, 0.1)

    def test_update_confidence_moves_toward_observed(self):
        c = C.update_confidence(0.2, 1.0, alpha=0.5)
        self.assertAlmostEqual(c, 0.6)
        c = C.update_confidence(0.6, 0.0, alpha=0.5)
        self.assertAlmostEqual(c, 0.3)

    def test_decay_by_age_fresh_unchanged(self):
        now = datetime.now(timezone.utc).isoformat()
        self.assertAlmostEqual(C.decay_by_age(0.9, now), 0.9, places=4)

    def test_decay_by_age_halflife(self):
        old = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        got = C.decay_by_age(1.0, old, halflife_days=90.0, floor=0.0)
        self.assertAlmostEqual(got, 0.5, places=2)

    def test_decay_by_age_floor(self):
        very_old = (datetime.now(timezone.utc) - timedelta(days=10000)).isoformat()
        got = C.decay_by_age(1.0, very_old, floor=0.15)
        self.assertGreaterEqual(got, 0.15)


if __name__ == "__main__":
    unittest.main()